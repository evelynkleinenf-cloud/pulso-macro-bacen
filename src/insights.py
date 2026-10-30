"""Respostas descritivas às perguntas oficiais; cálculos sem inferência causal."""

from itertools import combinations

import numpy as np
import pandas as pd
import streamlit as st

from src.analytics import correlation_input, correlation_matrix


@st.cache_data(ttl=3600)
def historical_exchange_mean(full: pd.DataFrame) -> float:
    """Referência fixa: média aritmética dos 60 fechamentos mensais do quinquênio."""
    return float(full["dolar"].mean())


@st.cache_data(ttl=3600)
def above_average_windows(full: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    """Intervalos selecionados e contíguos estritamente acima da referência fixa."""
    data = full.copy()
    above = (data["dolar"] > historical_exchange_mean(full)) & data["data"].isin(selected["data"])
    groups = (~above).cumsum()
    return (
        data.loc[above]
        .groupby(groups[above])
        .agg(
            inicio=("data", "min"),
            fim=("data", "max"),
            meses=("data", "size"),
            ptax_media=("dolar", "mean"),
        )
        .reset_index(drop=True)
    )


@st.cache_data(ttl=3600)
def lagged_inflation(full: pd.DataFrame, selected: pd.DataFrame, max_lag: int = 6) -> pd.DataFrame:
    """Pearson entre Δ PTAX_t (%) e IPCA mensal_(t+k); ambas as datas no recorte.

    A base completa tem calendário mensal validado. O shift precede o filtro:
    anos omitidos nunca viram meses adjacentes. Exigem-se 12 pares e variância.
    """
    data = full.set_index("data").sort_index()
    chosen = data.index.isin(pd.DatetimeIndex(selected["data"]))
    fx_change = data["dolar"].pct_change(fill_method=None) * 100
    rows = []
    for lag in range(max_lag + 1):
        target = data["ipca_mensal"].shift(-lag)
        target_chosen = pd.Series(chosen, index=data.index).shift(-lag, fill_value=False)
        pairs = pd.DataFrame({"cambio": fx_change, "inflacao": target}).loc[chosen & target_chosen].dropna()
        valid = len(pairs) >= 12 and pairs.nunique().gt(1).all()
        coefficient = float(pairs["cambio"].corr(pairs["inflacao"])) if valid else np.nan
        rows.append({"defasagem_meses": lag, "pares": len(pairs), "pearson": coefficient})
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def ranked_correlations(full: pd.DataFrame, selected: pd.DataFrame, changes: bool) -> pd.DataFrame:
    data = correlation_input(full, changes)
    data = data.loc[data["data"].isin(selected["data"])]
    columns = ("selic", "ipca_mensal", "ipca_12m", "dolar", "ibc_br")
    matrix = correlation_matrix(data, columns)
    rows = []
    for left, right in combinations(matrix.columns, 2):
        coefficient = matrix.loc[left, right]
        if pd.notna(coefficient):
            rows.append(
                {
                    "variavel_1": left,
                    "variavel_2": right,
                    "pearson": float(coefficient),
                    "pares": int(data[[left, right]].dropna().shape[0]),
                }
            )
    result = pd.DataFrame(rows, columns=["variavel_1", "variavel_2", "pearson", "pares"])
    if result.empty:
        return result
    return result.sort_values("pearson", key=lambda values: values.abs(), ascending=False).reset_index(
        drop=True
    )


@st.cache_data(ttl=3600)
def policy_windows(full: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    """Ciclo é a direção da última mudança mensal da meta, inclusive manutenção.

    A variação do IBC usa o fechamento anterior ao início de cada janela;
    na primeira competência da base, usa janeiro/2019 como ponto inicial.
    Recortes descontínuos sempre separam janelas.
    """
    data = full.sort_values("data").reset_index(drop=True)
    direction = np.sign(data["selic"].diff().round(8)).replace(0, np.nan).ffill().fillna(0)
    selected_mask = data["data"].isin(selected["data"])
    groups = (direction.ne(direction.shift()) | selected_mask.ne(selected_mask.shift())).cumsum()
    rows = []
    for _, window in data.loc[selected_mask].groupby(groups[selected_mask]):
        first, last = int(window.index[0]), int(window.index[-1])
        baseline = data.iloc[max(0, first - 1)]
        end = data.iloc[last]
        phase = {1: "Alta", -1: "Corte", 0: "Inicial / estável"}[int(direction.iloc[first])]
        rows.append(
            {
                "ciclo": phase,
                "inicio": window["data"].iloc[0],
                "fim": end["data"],
                "meses": len(window),
                "selic_inicial": float(baseline["selic"]),
                "selic_final": float(end["selic"]),
                "base_ibc": baseline["data"],
                "variacao_ibc_pct": float((end["ibc_br"] / baseline["ibc_br"] - 1) * 100),
            }
        )
    return pd.DataFrame(rows)
