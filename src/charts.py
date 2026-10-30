"""Gráficos Plotly Express: funções independentes da composição do Streamlit."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import correlation_input as correlation_input
from src.analytics import correlation_matrix
from src.config import LABELS

PALETTE = ["#35D4B0", "#7DA4FF", "#F4BB62", "#E879A8", "#A898EE"]


def style(figure: go.Figure, y_title: str | None = None) -> go.Figure:
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE,
        height=380,
        margin=dict(l=10, r=10, t=30, b=20),
        font=dict(family="Arial, sans-serif", color="#D5E0F0"),
        legend=dict(orientation="h", y=-0.22, x=0),
        xaxis_title=None,
        yaxis_title=y_title,
        hovermode="x unified",
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(150,170,200,0.12)")
    return figure


@st.cache_data(ttl=3600)
def calendar_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Insere NaN nos meses não selecionados para não desenhar pontes nas lacunas."""
    return (
        frame.set_index("data")
        .reindex(pd.date_range(frame["data"].min(), frame["data"].max(), freq="ME", name="data"))
        .reset_index()
    )


def interest_chart(frame: pd.DataFrame, columns: tuple[str, ...]) -> go.Figure:
    data = calendar_frame(frame)
    colors = {"selic": PALETTE[0], "ipca_12m": PALETTE[2], "juro_real_ex_post": PALETTE[1]}
    # Composição de figuras Express: barras do real e linhas das taxas nominais.
    figure = px.bar(data, x="data", y="juro_real_ex_post") if "juro_real_ex_post" in columns else go.Figure()
    if "juro_real_ex_post" in columns:
        figure.update_traces(
            name=LABELS["juro_real_ex_post"],
            showlegend=True,
            marker_color=colors["juro_real_ex_post"],
            opacity=0.55,
        )
    lines = [column for column in columns if column != "juro_real_ex_post"]
    if lines:
        curve = px.line(data, x="data", y=lines, color_discrete_map=colors)
        figure.add_traces(curve.data)
    for trace in figure.data:
        trace.name = LABELS.get(trace.name, trace.name)
        trace.hovertemplate = "%{x|%m/%Y}<br>%{y:.2f}%<extra>%{fullData.name}</extra>"
        if trace.type == "scatter":
            trace.update(connectgaps=False, line=dict(width=3))
    figure.add_hline(y=0, line_dash="dot", line_color="#708090")
    return style(figure, "Taxa (%)")


def exchange_chart(frame: pd.DataFrame, window: int, historical_mean: float | None = None) -> go.Figure:
    # Média sobre os meses do recorte, respeitando lacunas e exigindo janela completa.
    data = calendar_frame(frame)
    average = f"Média móvel de {window} meses"
    data[average] = data["dolar"].rolling(window, min_periods=window).mean()
    data = data.rename(columns={"dolar": "PTAX no fechamento mensal", "dolar_media": "PTAX média mensal"})
    figure = px.line(
        data,
        x="data",
        y=["PTAX no fechamento mensal", "PTAX média mensal", average],
        color_discrete_sequence=PALETTE,
    )
    figure.update_traces(connectgaps=False)
    figure.update_traces(line=dict(dash="dot"), selector={"name": "PTAX média mensal"})
    figure.update_traces(line=dict(dash="dash"), selector={"name": average})
    if historical_mean is not None:
        figure.add_hline(
            y=historical_mean,
            line_dash="dashdot",
            line_color=PALETTE[3],
            annotation_text=f"Média 2019–2023: R$ {historical_mean:.4f}",
            annotation_position="top left",
        )
    return style(figure, "R$/US$")


def scatter_chart(frame: pd.DataFrame) -> go.Figure:
    data = frame.assign(ano=frame["data"].dt.year.astype(str), competencia=frame["data"].dt.strftime("%m/%Y"))
    figure = px.scatter(
        data,
        x="dolar",
        y="ipca_12m",
        color="ano",
        size="selic",
        size_max=25,
        hover_name="competencia",
        labels={
            "dolar": "PTAX mensal (R$/US$)",
            "ipca_12m": "IPCA 12 meses (%)",
            "selic": "Selic (% a.a.)",
            "ano": "Ano",
        },
        color_discrete_sequence=PALETTE,
    )
    figure.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#0B1220")))
    style(figure, "IPCA em 12 meses (%)")
    figure.update_layout(hovermode="closest", xaxis_title="PTAX no fechamento mensal (R$/US$)")
    return figure


def activity_chart(frame: pd.DataFrame, normalized: bool) -> go.Figure:
    data = calendar_frame(frame)
    title = "IBC-Br (primeiro mês do recorte = 100)" if normalized else "IBC-Br (índice SGS)"
    if normalized:
        data["ibc_br"] = data["ibc_br"] / data["ibc_br"].dropna().iloc[0] * 100
    figure = px.line(data, x="data", y="ibc_br", color_discrete_sequence=[PALETTE[0]])
    figure.update_traces(line=dict(width=3), connectgaps=False)
    return style(figure, title)


def inflation_chart(frame: pd.DataFrame) -> go.Figure:
    data = frame.assign(sinal=np.where(frame["ipca_mensal"] >= 0, "Inflação", "Deflação"))
    figure = px.bar(
        data,
        x="data",
        y="ipca_mensal",
        color="sinal",
        labels={"sinal": "Variação", "ipca_mensal": "IPCA mensal (%)"},
        color_discrete_map={"Inflação": PALETTE[2], "Deflação": PALETTE[0]},
    )
    return style(figure, "IPCA mensal (%)")


def lag_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        frame.dropna(subset=["pearson"]),
        x="defasagem_meses",
        y="pearson",
        hover_data=["pares"],
        labels={
            "defasagem_meses": "Inflação observada k meses depois",
            "pearson": "Pearson r",
            "pares": "Pares válidos",
        },
        color_discrete_sequence=[PALETTE[0]],
    )
    style(figure, "Pearson r")
    figure.update_yaxes(range=[-1, 1])
    figure.update_xaxes(dtick=1, title="Defasagem k (meses)")
    return figure


def heatmap_chart(frame: pd.DataFrame, changes: bool) -> go.Figure | None:
    matrix = correlation_matrix(frame, ("selic", "ipca_mensal", "ipca_12m", "dolar", "ibc_br"))
    matrix = matrix.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if matrix.shape[0] < 2:
        return None
    names = {
        "selic": "Δ Selic (p.p.)" if changes else "Selic",
        "ipca_mensal": "Δ IPCA mensal (p.p.)" if changes else "IPCA mensal",
        "ipca_12m": "Δ IPCA 12m (p.p.)" if changes else "IPCA 12m",
        "dolar": "Δ PTAX (%)" if changes else "PTAX",
        "ibc_br": "Δ IBC-Br (%)" if changes else "IBC-Br",
    }
    matrix = matrix.rename(index=names, columns=names)
    figure = px.imshow(
        matrix,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        aspect="auto",
        color_continuous_scale=["#E879A8", "#17253B", "#35D4B0"],
        labels={"color": "Pearson"},
    )
    style(figure)
    figure.update_layout(hovermode="closest", height=430, yaxis_title=None)
    return figure
