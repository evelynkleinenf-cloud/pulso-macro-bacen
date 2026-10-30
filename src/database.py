"""PostgreSQL prioritário e contingência CSV, com validação idêntica."""

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import event, text

from src.analytics import prepare_dataframe
from src.config import BASE_COLUMNS, CSV_PATH, END_DATE, START_DATE, TABLE_NAME, VALUE_COLUMNS

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    frame: pd.DataFrame
    source: str
    notice: str | None = None


def get_database_settings() -> dict:
    """Única origem das credenciais: st.secrets. Nunca imprime valores secretos."""
    settings = dict(st.secrets["connections"]["postgresql"])
    if settings.get("dialect") != "postgresql":
        raise ValueError("Configure o dialect postgresql em st.secrets.")
    return settings


def _set_statement_timeout(connection) -> None:
    """Define o limite na transação; poolers podem ignorar opções de startup."""
    connection.exec_driver_sql("SET LOCAL statement_timeout = '5s'")


def get_connection():
    get_database_settings()
    connection = st.connection(
        "postgresql",
        type="sql",
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
    )
    if not event.contains(connection.engine, "begin", _set_statement_timeout):
        event.listen(connection.engine, "begin", _set_statement_timeout)
    return connection


@st.cache_data(ttl=3600)
def read_database() -> pd.DataFrame:
    connection = get_connection()
    # Nomes de tabela/colunas são constantes internas; valores usam parâmetros.
    columns = ", ".join(["data", *BASE_COLUMNS])
    frame = connection.query(
        f"SELECT {columns} FROM {TABLE_NAME} WHERE data BETWEEN :start AND :end ORDER BY data",
        params={"start": START_DATE, "end": END_DATE},
        # O cache externo de read_database já controla os 3600 segundos.
        ttl=0,
        show_spinner=False,
    )
    return prepare_dataframe(frame)


@st.cache_data(ttl=3600)
def read_local_csv(path: Path = CSV_PATH, file_version: int = 0) -> pd.DataFrame:
    """file_version recebe mtime_ns para invalidar o cache após uma atualização."""
    return prepare_dataframe(pd.read_csv(path, parse_dates=["data"]))


def load_dataset() -> LoadResult:
    """Tenta o banco em cada rerun; falhas não ficam presas no cache de fallback."""
    try:
        return LoadResult(frame=read_database(), source="PostgreSQL")
    except Exception as exc:
        # Fronteira de contingência: inclui segredo ausente, driver, rede e schema.
        # Não expor str(exc): mensagens de drivers podem conter dados de conexão.
        logger.info("PostgreSQL indisponível: %s. Usando CSV local.", type(exc).__name__)
    try:
        frame = read_local_csv(CSV_PATH, CSV_PATH.stat().st_mtime_ns)
    except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
        raise RuntimeError(
            "Não foi possível carregar o banco nem data/macro_mensal.csv. "
            "Execute python -m src.etl na raiz do projeto para gerar uma base válida."
        ) from exc
    return LoadResult(
        frame,
        "CSV local · BACEN/SGS",
        "Banco indisponível ou não configurado. Dados locais validados em uso.",
    )


def publish_database(frame: pd.DataFrame) -> None:
    """Cria a tabela do projeto e faz UPSERT transacional e idempotente."""
    validated = prepare_dataframe(frame)
    records = validated.astype(object).where(pd.notna(validated), None).to_dict("records")
    for record in records:
        record["data"] = record["data"].date()
    definitions = ", ".join(f"{name} DOUBLE PRECISION" for name in VALUE_COLUMNS)
    columns = ["data", *VALUE_COLUMNS]
    placeholders = ", ".join(f":{name}" for name in columns)
    updates = ", ".join(f"{name} = EXCLUDED.{name}" for name in VALUE_COLUMNS)
    try:
        connection = get_connection()
        with connection.engine.begin() as transaction:
            transaction.execute(
                text(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (data DATE PRIMARY KEY, {definitions})")
            )
            transaction.execute(
                text(
                    f"INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders}) "
                    f"ON CONFLICT (data) DO UPDATE SET {updates}"
                ),
                records,
            )
        read_database.clear()
    except Exception as exc:
        raise RuntimeError(
            "Falha ao publicar no PostgreSQL. Revise st.secrets, permissões e conectividade."
        ) from exc
