"""Transformações compartilhadas pelo ETL, banco, notebook e interface."""

import numpy as np
import pandas as pd
import streamlit as st

from src.config import BASE_COLUMNS, END_DATE, START_DATE, VALUE_COLUMNS


@st.cache_data(ttl=3600)
def prepare_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Valida o contrato e recalcula derivados sem preencher lacunas silenciosamente."""
    required = {"data", *BASE_COLUMNS}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}.")
    result = frame.loc[:, ["data", *BASE_COLUMNS]].copy()
    result["data"] = pd.to_datetime(result["data"], errors="raise")
    if result["data"].isna().any() or result["data"].dt.tz is not None:
        raise ValueError("Datas ausentes ou com fuso horário não são permitidas.")
    result["data"] = result["data"].astype("datetime64[ns]")
    result = result.sort_values("data").reset_index(drop=True)
    if result["data"].duplicated().any():
        raise ValueError("Existem competências mensais duplicadas.")
    month_ends = result["data"] + pd.offsets.MonthEnd(0)
    if not result["data"].equals(month_ends):
        raise ValueError("As datas devem representar o último dia de cada mês.")
    if result.empty:
        raise ValueError("A base está vazia.")
    expected = pd.date_range(START_DATE, END_DATE, freq="ME")
    if not pd.DatetimeIndex(result["data"]).equals(expected):
        raise ValueError("A base deve conter todos os 60 meses de janeiro/2019 a dezembro/2023.")
    for column in BASE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="raise").astype(float)
    if not np.isfinite(result[BASE_COLUMNS].to_numpy()).all():
        raise ValueError("A base contém valores ausentes ou não finitos.")
    if (result[["dolar", "dolar_media", "ibc_br"]] <= 0).any().any():
        raise ValueError("Câmbio e IBC-Br devem ser positivos.")
    if (result[["selic", "ipca_mensal", "ipca_12m", "selic_acumulada_12m"]] <= -100).any().any():
        raise ValueError("Taxas inferiores ou iguais a -100% são inválidas.")
    result["juro_real_ex_post"] = (
        (1 + result["selic_acumulada_12m"] / 100) / (1 + result["ipca_12m"] / 100) - 1
    ) * 100
    # A primeira variação permanece ausente: o contrato final começa em janeiro/2019.
    result["ibc_br_variacao_mensal"] = result["ibc_br"].pct_change(fill_method=None) * 100
    return result.loc[:, ["data", *VALUE_COLUMNS]]


@st.cache_data(ttl=3600)
def filter_dataframe(frame: pd.DataFrame, start: str, end: str, years: tuple[int, ...]) -> pd.DataFrame:
    mask = frame["data"].between(pd.Timestamp(start), pd.Timestamp(end))
    mask &= frame["data"].dt.year.isin(years)
    return frame.loc[mask].copy()


@st.cache_data(ttl=3600)
def correlation_matrix(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    """Exclui séries constantes; Pearson só é definido com variância positiva."""
    selected = frame.loc[:, list(columns)]
    selected = selected.loc[:, selected.nunique(dropna=True) > 1]
    return selected.corr(method="pearson", min_periods=3)


@st.cache_data(ttl=3600)
def correlation_input(frame: pd.DataFrame, changes: bool) -> pd.DataFrame:
    """Transforma antes do recorte, preservando a competência anterior real."""
    data = frame[["data", "selic", "ipca_mensal", "ipca_12m", "dolar", "ibc_br"]].copy()
    if changes:
        rates = ["selic", "ipca_mensal", "ipca_12m"]
        data[rates] = data[rates].diff()
        data[["dolar", "ibc_br"]] = data[["dolar", "ibc_br"]].pct_change(fill_method=None) * 100
    return data


@st.cache_data(ttl=3600)
def export_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False, sep=";", decimal=",", date_format="%Y-%m-%d").encode("utf-8-sig")


def metric_values(frame: pd.DataFrame, column: str) -> tuple[float, float | None]:
    """Último valor e diferença para a observação anterior dentro do recorte."""
    values = frame[column].dropna()
    if values.empty:
        raise ValueError(f"Não há observações para {column}.")
    delta = float(values.iloc[-1] - values.iloc[-2]) if len(values) > 1 else None
    return float(values.iloc[-1]), delta
