"""Extração reprodutível do SGS: python -m src.etl [--use-raw] [--to-db]."""

import argparse
import hashlib
import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.analytics import prepare_dataframe
from src.config import (
    API_URL,
    CSV_PATH,
    END_DATE,
    FETCH_START_DATE,
    METADATA_PATH,
    RAW_DIR,
    SERIES,
    START_DATE,
)

logger = logging.getLogger(__name__)


def create_http_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "ProjetoAnalyticsBACEN/1.0"})
    return session


@st.cache_data(ttl=3600)
def fetch_series(code: int, start: date, end: date) -> list[dict[str, str]]:
    """Consulta intervalos anuais, abaixo do limite de 10 anos do SGS diário."""
    records: list[dict[str, str]] = []
    with create_http_session() as session:
        for year in range(start.year, end.year + 1):
            lower, upper = max(start, date(year, 1, 1)), min(end, date(year, 12, 31))
            response = session.get(
                API_URL.format(code=code),
                params={
                    "formato": "json",
                    "dataInicial": lower.strftime("%d/%m/%Y"),
                    "dataFinal": upper.strftime("%d/%m/%Y"),
                },
                timeout=(10, 45),
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list) or not payload:
                raise ValueError(f"SGS {code}: resposta vazia ou fora do contrato em {year}.")
            if any(not isinstance(row, dict) or not {"data", "valor"} <= row.keys() for row in payload):
                raise ValueError(f"SGS {code}: campos data/valor ausentes.")
            records.extend(payload)
    return records


@st.cache_data(ttl=3600)
def parse_series(records: list[dict[str, str]], name: str) -> pd.Series:
    frame = pd.DataFrame(records)
    if frame.empty or not {"data", "valor"} <= set(frame.columns):
        raise ValueError(f"Série {name} vazia ou com campos inválidos.")
    frame["data"] = pd.to_datetime(frame["data"], format="%d/%m/%Y", errors="raise")
    frame["valor"] = pd.to_numeric(
        frame["valor"].astype(str).str.replace(",", ".", regex=False), errors="raise"
    )
    if frame["data"].isna().any() or not np.isfinite(frame["valor"]).all():
        raise ValueError(f"Série {name} contém valores inválidos.")
    if frame["data"].duplicated().any():
        raise ValueError(f"Série {name} contém datas duplicadas.")
    return frame.sort_values("data").set_index("data")["valor"].rename(name)


@st.cache_data(ttl=3600)
def build_monthly_dataset(raw: dict[str, list[dict[str, str]]]) -> pd.DataFrame:
    """Alinha frequências; não interpola inflação, câmbio ou atividade."""
    parsed = {name: parse_series(raw[name], name) for name in SERIES}
    monthly = pd.DataFrame(index=pd.date_range(START_DATE, END_DATE, freq="ME", name="data"))
    monthly["selic"] = parsed["selic"].resample("ME").last()
    monthly["dolar"] = parsed["dolar"].resample("ME").last()
    monthly["dolar_media"] = parsed["dolar"].resample("ME").mean()
    for name in ("ipca_mensal", "ipca_12m", "ibc_br"):
        periods = parsed[name].index.to_period("M")
        if periods.duplicated().any():
            raise ValueError(f"Série {name} contém mais de um registro na mesma competência.")
        monthly[name] = parsed[name].resample("ME").last()

    # A meta anual é convertida em fator diário ACT/365. O carry só usa o passado.
    # Não representa o retorno efetivo da Selic overnight: é uma proxy com a série 432.
    daily_index = pd.date_range(date(2018, 1, 1), END_DATE, freq="D")
    target = parsed["selic"]
    if (target <= -100).any():
        raise ValueError("Meta Selic inválida para capitalização.")
    calendar_target = (
        target.reindex(target.index.union(daily_index)).sort_index().ffill().reindex(daily_index)
    )
    if calendar_target.isna().any():
        raise ValueError("Histórico Selic insuficiente para o cálculo dos juros em 12 meses.")
    cumulative = (np.log1p(calendar_target / 100) / 365).cumsum()
    prior_dates = monthly.index - pd.DateOffset(years=1)
    log_factors = cumulative.reindex(monthly.index).to_numpy() - cumulative.reindex(prior_dates).to_numpy()
    monthly["selic_acumulada_12m"] = np.expm1(log_factors) * 100
    return prepare_dataframe(monthly.reset_index())


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(content)
    temp.replace(path)


def run_etl(use_raw: bool = False, to_db: bool = False) -> pd.DataFrame:
    raw: dict[str, list[dict[str, str]]] = {}
    for name, definition in SERIES.items():
        path = RAW_DIR / f"sgs_{definition['code']}.json"
        if use_raw:
            raw[name] = json.loads(path.read_text(encoding="utf-8"))
        else:
            start = FETCH_START_DATE if name == "selic" else START_DATE
            logger.info("Extraindo SGS %s (%s)", definition["code"], name)
            raw[name] = fetch_series(definition["code"], start, END_DATE)
    frame = build_monthly_dataset(raw)
    # Só publica o snapshot após todas as cinco séries passarem na validação.
    for name, definition in SERIES.items():
        atomic_write(
            RAW_DIR / f"sgs_{definition['code']}.json",
            json.dumps(raw[name], ensure_ascii=False, indent=2).encode("utf-8"),
        )
    payload = frame.to_csv(index=False, date_format="%Y-%m-%d", float_format="%.10f").encode("utf-8")
    atomic_write(CSV_PATH, payload)
    metadata = {
        "source": "Banco Central do Brasil / SGS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "period": {"start": START_DATE.isoformat(), "end": END_DATE.isoformat()},
        "rows": len(frame),
        "sha256_csv": hashlib.sha256(payload).hexdigest(),
        "raw_observations": {name: len(records) for name, records in raw.items()},
        "series": SERIES,
        "methodology": {
            "monthly_date": "Último dia do mês; não representa a data de divulgação.",
            "selic": "Última meta do mês (% a.a.). Histórico auxiliar desde dezembro/2017.",
            "dolar": "Última PTAX de venda observada no mês (R$/US$).",
            "dolar_media": "Média aritmética das PTAX de venda observadas no mês.",
            "selic_acumulada_12m": "Produto diário de (1 + meta/100)^(1/365) nos 12 meses anteriores, calendário ACT/365.",
            "juro_real_ex_post": "100 * ((1 + selic_acumulada_12m/100) / (1 + ipca_12m/100) - 1). Proxy pela meta, não retorno overnight.",
            "ibc_br": "SGS 24364 com ajuste sazonal; série revisável. Unidade conservada conforme o SGS.",
            "missing": "Sem interpolação; apenas meta Selic carregada para dias sem nova observação.",
            "vintage": "Snapshot atual de séries históricas revisáveis, não uma base em tempo real de 2019–2023.",
        },
    }
    atomic_write(METADATA_PATH, json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8"))
    if to_db:
        from src.database import publish_database

        publish_database(frame)
    logger.info("Base validada: %s meses em %s", len(frame), CSV_PATH)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--use-raw", action="store_true", help="Reprocessa os JSON locais, sem consultar a API."
    )
    parser.add_argument("--to-db", action="store_true", help="Publica no PostgreSQL usando st.secrets.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run_etl(use_raw=args.use_raw, to_db=args.to_db)
    except (requests.RequestException, ValueError, OSError, KeyError, RuntimeError) as exc:
        logger.error("ETL não concluído (%s). Revise a conexão e os arquivos de entrada.", type(exc).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
