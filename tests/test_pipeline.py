"""Testes sem rede: contrato, cálculo financeiro e contingência de dados."""

import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
import requests

from src import database
from src.analytics import correlation_matrix, export_csv, filter_dataframe, metric_values, prepare_dataframe
from src.charts import calendar_frame, correlation_input, heatmap_chart
from src.config import CSV_PATH, METADATA_PATH, RAW_DIR, SERIES
from src.etl import build_monthly_dataset, create_http_session, fetch_series, parse_series


@pytest.fixture
def frame():
    return prepare_dataframe(pd.read_csv(CSV_PATH))


@pytest.fixture
def raw():
    return {
        name: json.loads((RAW_DIR / f"sgs_{definition['code']}.json").read_text(encoding="utf-8"))
        for name, definition in SERIES.items()
    }


def test_real_snapshot_contract_and_provenance(frame):
    import hashlib

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert len(frame) == 60
    assert frame["data"].iloc[0] == pd.Timestamp("2019-01-31")
    assert frame["data"].iloc[-1] == pd.Timestamp("2023-12-31")
    assert metadata["sha256_csv"] == hashlib.sha256(CSV_PATH.read_bytes()).hexdigest()
    # Valores históricos oficiais conhecidos: detectam troca de série ou frequência.
    december = frame.iloc[-1]
    assert december["selic"] == pytest.approx(11.75)
    assert december["ipca_12m"] == pytest.approx(4.62)
    assert december["ipca_mensal"] == pytest.approx(0.56)


def test_raw_reprocessing_matches_csv(frame, raw):
    rebuilt = build_monthly_dataset(raw)
    pd.testing.assert_frame_equal(rebuilt, frame, check_exact=False, rtol=1e-8, atol=1e-8)


def test_daily_capitalization_and_fisher_are_retrospective(frame, raw):
    # Implementação independente para 2020: janela de 366 dias, sem usar taxa terminal.
    target = parse_series(raw["selic"], "selic")
    dates = pd.date_range("2020-01-01", "2020-12-31", freq="D")
    levels = target.reindex(target.index.union(dates)).sort_index().ffill().reindex(dates)
    nominal = (np.prod((1 + levels.to_numpy() / 100) ** (1 / 365)) - 1) * 100
    observed = frame.loc[frame["data"] == "2020-12-31"].iloc[0]
    assert observed["selic_acumulada_12m"] == pytest.approx(nominal, abs=1e-8)
    assert observed["juro_real_ex_post"] == pytest.approx(
        ((1 + nominal / 100) / (1 + observed["ipca_12m"] / 100) - 1) * 100, abs=1e-8
    )
    assert nominal != pytest.approx(observed["selic"])


@pytest.mark.parametrize(
    "problem", ["missing_column", "duplicate", "missing_month", "nan", "negative_fx", "wrong_date"]
)
def test_rejects_invalid_data(frame, problem):
    broken = frame.copy()
    if problem == "missing_column":
        broken = broken.drop(columns="ipca_12m")
    elif problem == "duplicate":
        broken = pd.concat([broken, broken.iloc[[0]]])
    elif problem == "missing_month":
        broken = broken.iloc[1:]
    elif problem == "nan":
        broken.loc[0, "selic"] = np.nan
    elif problem == "negative_fx":
        broken.loc[0, "dolar"] = -1
    else:
        broken.loc[0, "data"] = pd.Timestamp("2019-01-01")
    with pytest.raises(ValueError):
        prepare_dataframe(broken)


def test_filters_metrics_and_csv_agree(frame):
    selected = filter_dataframe(frame, "2021-06-30", "2022-03-31", (2021, 2022))
    assert len(selected) == 10
    value, delta = metric_values(selected, "dolar")
    assert value == selected["dolar"].iloc[-1]
    assert delta == pytest.approx(selected["dolar"].iloc[-1] - selected["dolar"].iloc[-2])
    from io import BytesIO

    payload = export_csv(selected)
    assert payload.startswith(b"\xef\xbb\xbf")
    decoded = pd.read_csv(BytesIO(payload), sep=";", decimal=",")
    assert len(decoded) == 10
    assert decoded["dolar"].iloc[-1] == pytest.approx(value)
    assert metric_values(selected.iloc[[0]], "selic")[1] is None


def test_missing_years_break_lines_and_do_not_distort_changes(frame):
    selected = frame.loc[frame["data"].dt.year.isin([2019, 2023])]
    calendar = calendar_frame(selected)
    assert calendar.loc[calendar["data"].dt.year == 2021, "dolar"].isna().all()
    changes = correlation_input(frame, True)
    jan23 = changes.loc[changes["data"] == "2023-01-31", "dolar"].iloc[0]
    actual = frame.set_index("data")["dolar"]
    assert jan23 == pytest.approx((actual.loc["2023-01-31"] / actual.loc["2022-12-31"] - 1) * 100)


def test_correlation_handles_insufficient_or_constant_series(frame):
    assert heatmap_chart(frame.iloc[:1], False) is None
    constant = frame.copy()
    constant["selic"] = 10.0
    matrix = correlation_matrix(constant, ("selic", "dolar", "ipca_12m"))
    assert "selic" not in matrix.columns
    assert heatmap_chart(correlation_input(frame, True), True) is not None


def test_database_is_preferred(frame, monkeypatch):
    monkeypatch.setattr(database, "read_database", lambda: frame)
    monkeypatch.setattr(database, "read_local_csv", Mock(side_effect=AssertionError("CSV desnecessário")))
    result = database.load_dataset()
    assert result.source == "PostgreSQL"
    assert result.notice is None


def test_publishing_is_idempotent_and_updates_values(frame, monkeypatch):
    # Exercita o DDL/UPSERT comum aos dois dialetos sem exigir servidor no CI.
    # O driver e a conexão PostgreSQL ainda precisam de validação no destino.
    from types import SimpleNamespace

    from sqlalchemy import create_engine, text

    engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(database, "get_connection", lambda: SimpleNamespace(engine=engine))
    database.publish_database(frame)
    changed = frame.copy()
    changed.loc[changed.index[-1], "dolar"] = 5.1234
    database.publish_database(changed)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM indicadores_macro")).scalar_one() == 60
        last = connection.execute(
            text("SELECT dolar FROM indicadores_macro ORDER BY data DESC LIMIT 1")
        ).scalar_one()
        assert last == pytest.approx(5.1234)
    engine.dispose()


@pytest.mark.parametrize(
    "error", [ConnectionError("offline"), KeyError("connections"), ValueError("schema inválido")]
)
def test_database_failure_falls_back(frame, monkeypatch, error):
    monkeypatch.setattr(database, "read_database", Mock(side_effect=error))
    result = database.load_dataset()
    pd.testing.assert_frame_equal(result.frame, frame)
    assert result.source.startswith("CSV local")


def test_both_sources_fail_with_actionable_message(monkeypatch):
    monkeypatch.setattr(database, "read_database", Mock(side_effect=ConnectionError("secret=value")))
    monkeypatch.setattr(database, "CSV_PATH", Path("data/arquivo_ausente.csv"))
    with pytest.raises(RuntimeError, match="python -m src.etl") as error:
        database.load_dataset()
    assert "secret=value" not in str(error.value)


def test_fetch_uses_yearly_windows(monkeypatch):
    from datetime import date

    calls = []

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url, params, timeout):
            calls.append(params)
            response = Mock()
            response.json.return_value = [{"data": params["dataInicial"], "valor": "1.0"}]
            return response

    monkeypatch.setattr("src.etl.create_http_session", Session)
    fetch_series.clear()
    records = fetch_series(99999, date(2019, 6, 1), date(2021, 2, 1))
    assert len(records) == 3
    assert calls[0]["dataInicial"] == "01/06/2019"
    assert calls[0]["dataFinal"] == "31/12/2019"
    assert calls[-1]["dataFinal"] == "01/02/2021"


def test_retry_policy_is_finite_and_read_only():
    with create_http_session() as session:
        retry = session.get_adapter("https://").max_retries
        assert retry.total == 3
        assert retry.allowed_methods == frozenset({"GET"})
        assert 429 in retry.status_forcelist


def test_http_error_is_not_accepted_as_data(monkeypatch):
    from datetime import date

    session = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)
    session.get.return_value.raise_for_status.side_effect = requests.HTTPError("503")
    monkeypatch.setattr("src.etl.create_http_session", lambda: session)
    fetch_series.clear()
    with pytest.raises(requests.HTTPError):
        fetch_series(99998, date(2023, 1, 1), date(2023, 12, 31))
