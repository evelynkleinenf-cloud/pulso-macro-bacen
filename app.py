"""Dashboard de macroeconomia. Execute: streamlit run app.py na raiz."""

import json
import logging

import pandas as pd
import streamlit as st

from src.analytics import export_csv, filter_dataframe, metric_values
from src.charts import (
    activity_chart,
    correlation_input,
    exchange_chart,
    heatmap_chart,
    inflation_chart,
    interest_chart,
    lag_chart,
    scatter_chart,
)
from src.config import LABELS, METADATA_PATH, SERIES
from src.database import load_dataset
from src.insights import (
    above_average_windows,
    historical_exchange_mean,
    lagged_inflation,
    policy_windows,
    ranked_correlations,
)

st.set_page_config(
    page_title="Pulso Macro | BACEN", page_icon="📊", layout="wide", initial_sidebar_state="expanded"
)
logger = logging.getLogger(__name__)


def br_number(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def reset_filters() -> None:
    for key in ("anos", "periodo", "juros", "janela", "normalizar", "correlacao"):
        st.session_state.pop(key, None)


def sidebar(frame: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...], int, bool, bool]:
    with st.sidebar:
        st.markdown("### ◈ PULSO MACRO")
        st.caption("BRASIL · BACEN / SGS")
        st.divider()
        st.markdown("#### Explore o período")
        years = sorted(frame["data"].dt.year.unique().tolist())
        chosen_years = st.multiselect("Anos", years, default=years, key="anos")
        if not chosen_years:
            st.info("Selecione pelo menos um ano para explorar os indicadores.")
            st.button("Restaurar filtros", key="reset_empty", on_click=reset_filters, width="stretch")
            st.stop()
        options = frame.loc[frame["data"].dt.year.isin(chosen_years), "data"].dt.date.tolist()
        current = st.session_state.get("periodo")
        if current is not None and any(value not in options for value in current):
            st.session_state.pop("periodo", None)
        start, end = st.select_slider(
            "Competências",
            options=options,
            value=(options[0], options[-1]),
            format_func=lambda value: value.strftime("%m/%Y"),
            key="periodo",
        )
        st.divider()
        st.markdown("#### Ajuste a análise")
        selected = st.multiselect(
            "Curvas de juros e inflação",
            ["selic", "juro_real_ex_post", "ipca_12m"],
            default=["selic", "juro_real_ex_post", "ipca_12m"],
            format_func=lambda value: LABELS[value],
            key="juros",
        )
        window = st.selectbox("Média móvel da PTAX (meses)", [3, 6, 12], key="janela")
        normalized = st.toggle("Rebasear IBC-Br em 100", value=False, key="normalizar")
        mode = st.radio(
            "Correlação de Pearson",
            ["Variações mensais", "Níveis"],
            key="correlacao",
            help="Variações reduzem o efeito de tendências comuns, mas não demonstram causalidade.",
        )
        st.divider()
        st.button("Restaurar filtros", on_click=reset_filters, width="stretch")
        st.caption("Os filtros atualizam KPIs, gráficos, tabela e exportação.")
    return (
        filter_dataframe(frame, str(start), str(end), tuple(chosen_years)),
        tuple(selected),
        window,
        normalized,
        mode == "Variações mensais",
    )


def draw_metrics(frame: pd.DataFrame) -> None:
    st.caption(
        f"REFERÊNCIA: {frame['data'].iloc[-1]:%m/%Y} · "
        "Deltas contra a observação anterior do recorte. Taxas em p.p.; câmbio em reais por dólar."
    )
    # Duas linhas mantêm valores monetários legíveis em janelas menores.
    cards = [column for _ in range(2) for column in st.columns(2)]
    definitions = [
        ("Meta Selic", "selic", "%", "p.p.", "Meta anual no fechamento do mês (SGS 432)."),
        ("IPCA em 12 meses", "ipca_12m", "%", "p.p.", "Inflação acumulada oficial em 12 meses (SGS 13522)."),
        (
            "Juro real · proxy",
            "juro_real_ex_post",
            "%",
            "p.p.",
            "Fisher entre a meta Selic capitalizada nos 12 meses anteriores e o IPCA de 12 meses. Aproximação pela meta, não retorno realizado.",
        ),
        ("Dólar PTAX", "dolar", "", "BRL/USD", "PTAX de venda na última observação do mês (SGS 1)."),
    ]
    for card, (label, column, suffix, delta_unit, help_text) in zip(cards, definitions):
        value, delta = metric_values(frame, column)
        formatted = f"R$ {br_number(value)}" if column == "dolar" else f"{br_number(value)}{suffix}"
        formatted_delta = None if delta is None else f"{br_number(delta)} {delta_unit}"
        card.metric(label, formatted, delta=formatted_delta, delta_color="off", help=help_text, border=True)
    if len(frame) == 1:
        st.caption("Uma competência selecionada: não há observação anterior para calcular os deltas.")
    elif (frame["data"].iloc[-1].to_period("M") - frame["data"].iloc[-2].to_period("M")).n != 1:
        st.caption("O delta compara meses não consecutivos porque há uma lacuna nos anos selecionados.")


def draw_answers(full: pd.DataFrame, frame: pd.DataFrame, changes: bool) -> None:
    st.subheader("O que os indicadores respondem")
    st.caption(
        "Resultados calculados para os filtros atuais. Evidência descritiva para planejamento de cenários."
    )
    peak = frame.loc[frame["juro_real_ex_post"].idxmax()]
    start, end = frame.iloc[0], frame.iloc[-1]
    st.markdown("#### 1. Como evoluíram os juros e quando o juro real foi maior?")
    st.write(
        f"A meta Selic passa de {br_number(start.selic)}% em {start.data:%m/%Y} para "
        f"{br_number(end.selic)}% em {end.data:%m/%Y}. O maior juro real retrospectivo do recorte "
        f"é {br_number(peak.juro_real_ex_post)}% em {peak.data:%m/%Y}."
    )
    st.caption(
        "Uso: comparar ambientes de custo de capital. A proxy pela meta não é o retorno efetivo de uma aplicação."
    )

    st.markdown("#### 2. Quando o dólar ficou acima da média histórica?")
    mean = historical_exchange_mean(full)
    windows = above_average_windows(full, frame)
    months = int((frame["dolar"] > mean).sum())
    st.write(
        f"A referência fixa de 2019–2023 é R$ {br_number(mean, 4)}, média dos 60 fechamentos mensais. "
        f"No recorte, {months} de {len(frame)} competências ficam acima dessa referência."
    )
    if windows.empty:
        st.info("Nenhuma competência selecionada supera a média histórica.")
    else:
        st.dataframe(
            windows.assign(inicio=windows.inicio.dt.strftime("%m/%Y"), fim=windows.fim.dt.strftime("%m/%Y"))
            .rename(
                columns={
                    "inicio": "Início",
                    "fim": "Fim",
                    "meses": "Meses",
                    "ptax_media": "PTAX média da janela",
                }
            )
            .round(4),
            hide_index=True,
            width="stretch",
        )
    st.caption(
        "Uso: testar a sensibilidade de despesas e receitas em dólar; média histórica não é uma previsão de câmbio."
    )

    st.markdown("#### 3. A desvalorização cambial se associa à inflação posterior?")
    lagged = lagged_inflation(full, frame)
    valid = lagged.dropna(subset=["pearson"])
    if valid.empty:
        st.info(
            "Selecione uma janela maior: cada correlação exige ao menos 12 pares mensais e variância nas duas séries."
        )
    else:
        best = valid.loc[valid.pearson.abs().idxmax()]
        st.write(
            f"Entre as defasagens exploradas, a maior associação em módulo é r = {br_number(best.pearson, 3)} "
            f"em k = {int(best.defasagem_meses)} mês(es), com {int(best.pares)} pares. "
            "k = 0 mede o mesmo mês; k > 0 compara a variação da PTAX com o IPCA mensal posterior."
        )
        st.plotly_chart(lag_chart(lagged), width="stretch", key="lag_plot")
    st.dataframe(
        lagged.rename(
            columns={
                "defasagem_meses": "Defasagem k (meses)",
                "pares": "Pares válidos",
                "pearson": "Pearson r",
            }
        ).round(3),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Δ PTAX = variação percentual do fechamento mensal; sinal positivo indica desvalorização do real. "
        "Ambas as competências precisam estar selecionadas. Estudo exploratório de 0 a 6 meses, sem teste "
        "de significância ou controle de autocorrelação, sazonalidade e choques comuns. A escolha do maior "
        "|r| entre várias janelas não comprova repasse cambial nem causalidade."
    )

    st.markdown("#### 4. Como a atividade se comportou nos ciclos de juros?")
    cycles = policy_windows(full, frame)
    st.dataframe(
        cycles.assign(
            inicio=cycles.inicio.dt.strftime("%m/%Y"),
            fim=cycles.fim.dt.strftime("%m/%Y"),
            base_ibc=cycles.base_ibc.dt.strftime("%m/%Y"),
        )
        .rename(
            columns={
                "ciclo": "Ciclo",
                "inicio": "Início",
                "fim": "Fim",
                "meses": "Meses",
                "selic_inicial": "Selic inicial (%)",
                "selic_final": "Selic final (%)",
                "base_ibc": "Base IBC-Br",
                "variacao_ibc_pct": "Variação IBC-Br (%)",
            }
        )
        .round(2),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Ciclo = direção da última mudança mensal da meta, incluindo meses de manutenção. "
        "O IBC-Br compara o fechamento final à competência anterior ao início da janela; em janeiro/2019, "
        "usa a primeira observação disponível. Lacunas nos filtros separam janelas. "
        "Uso: contextualizar cenários de demanda; a comparação não isola o efeito dos juros."
    )

    st.markdown("#### 5. Quais pares apresentam maior correlação?")
    ranking = ranked_correlations(full, frame, changes)
    mode = "variações mensais" if changes else "níveis"
    if ranking.empty:
        st.info("Não há pares suficientes com variância para ordenar as correlações.")
    else:
        labels = {name: definition["label"] for name, definition in SERIES.items()}
        top = ranking.iloc[0]
        st.write(
            f"Em {mode}, o maior |r| é entre {labels[top.variavel_1]} e {labels[top.variavel_2]}: r = {br_number(top.pearson, 3)}, com {int(top.pares)} pares."
        )
        st.dataframe(
            ranking.head(5)
            .assign(
                variavel_1=lambda data: data.variavel_1.map(labels),
                variavel_2=lambda data: data.variavel_2.map(labels),
            )
            .rename(
                columns={
                    "variavel_1": "Indicador 1",
                    "variavel_2": "Indicador 2",
                    "pearson": "Pearson r",
                    "pares": "Pares válidos",
                }
            )
            .round(3),
            hide_index=True,
            width="stretch",
        )
    st.caption(
        "Ordenação por |r|, preservando o sinal. Nas variações, taxas usam p.p.; câmbio e IBC-Br usam %. Tendências comuns podem elevar correlações em níveis."
    )
    st.info(
        "Decisão apoiada: priorizar testes de sensibilidade de juros, câmbio e demanda no planejamento. O painel não prevê preços nem recomenda investimentos."
    )


def methodology() -> None:
    st.markdown("#### Como os dados foram preparados")
    st.markdown(
        "A base reúne **60 competências mensais, de janeiro de 2019 a dezembro de 2023**. "
        "Selic e PTAX usam a última observação de cada mês. A média mensal da PTAX usa somente "
        "as observações publicadas. IPCA e IBC-Br preservam a competência original, sem interpolação. "
        "As datas na base representam o fim da competência, e não o dia de divulgação."
    )
    st.latex(r"r_{real,12m} = \left[\frac{1+r_{meta,12m}/100}{1+\pi_{12m}/100}-1\right]\times100")
    st.markdown(
        "**Juro real ex-post — proxy:** a meta Selic (SGS 432) é capitalizada diariamente, "
        "usando o fator `(1 + meta/100)^(1/365)`, nos 12 meses terminados em cada competência. "
        "A meta vigente é mantida em fins de semana e feriados. O histórico auxiliar desde "
        "dezembro/2017 permite calcular todo o ano de 2019. A convenção é ACT/365, inclusive "
        "em anos bissextos. O resultado é deflacionado pelo IPCA acumulado oficial (SGS 13522). "
        "**A série 432 é uma meta: este indicador aproxima o juro real e não mede o retorno "
        "efetivo de uma aplicação ou da Selic overnight.**"
    )
    st.markdown(
        "**IBC-Br:** a série 24364 já possui ajuste sazonal. A escala original é preservada; "
        "o botão de rebaseamento altera apenas a visualização. O IBC-Br é um indicador de atividade, "
        "não substitui o PIB. As séries históricas podem ser revisadas pelo Banco Central. "
        "O snapshot representa os valores disponíveis na extração, não as informações disponíveis "
        "à época de cada decisão econômica."
    )
    st.markdown(
        "**Correlação:** Pearson mede associação linear contemporânea. Na opção de variações, "
        "as taxas usam diferenças em pontos percentuais; câmbio e IBC-Br usam variações percentuais. "
        "As transformações são feitas antes dos filtros. Séries constantes são excluídas e "
        "exigem-se pelo menos três pares válidos. Tendências, defasagens e fatores omitidos "
        "limitam a interpretação; correlação não demonstra causalidade."
    )
    catalog = pd.DataFrame(
        [
            {
                "Série SGS": definition["code"],
                "Indicador": definition["label"],
                "Unidade": definition["unit"],
                "Frequência de origem": definition["frequency"],
            }
            for definition in SERIES.values()
        ]
    )
    st.dataframe(catalog, hide_index=True, width="stretch")
    st.markdown(
        "Fontes: [API SGS / Banco Central](https://dadosabertos.bcb.gov.br/) · "
        "[Metadados do IBC-Br 24364](https://www3.bcb.gov.br/sgspub/consultarmetadados/consultarMetadadosSeries.do?method=consultarMetadadosSeriesInternet&hdOidSerieSelecionada=24364) · "
        "[Conexões Streamlit](https://docs.streamlit.io/develop/api-reference/connections/st.connection)"
    )


def main() -> None:
    try:
        with st.spinner("Carregando indicadores…"):
            loaded = load_dataset()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    frame, interest_columns, window, normalized, changes = sidebar(loaded.frame)
    st.caption("OBSERVATÓRIO ECONÔMICO / LINHA 3")
    st.title("Pulso Macro")
    st.markdown("Juros, inflação, câmbio e atividade econômica do Brasil em uma visão integrada.")
    st.caption(
        "Pergunta orientadora: como os ciclos macroeconômicos se relacionam e o que observar ao planejar cenários de custos e demanda?"
    )
    st.caption(
        f"{frame['data'].min():%m/%Y} → {frame['data'].max():%m/%Y} · "
        f"{len(frame)} competências selecionadas · Fonte em uso: {loaded.source}"
    )
    if loaded.notice:
        st.info(loaded.notice, icon="ℹ️")
    draw_metrics(frame)
    st.write("")
    overview, activity, relations, dataset, methods, answers = st.tabs(
        ["Panorama", "Preços & atividade", "Relações", "Base de dados", "Metodologia", "Respostas de negócio"]
    )
    with overview:
        st.subheader("O ciclo dos juros e da inflação")
        st.caption(
            "Selic: meta anual vigente. Juro real: aproximação retrospectiva em 12 meses; as curvas têm horizontes distintos."
        )
        if interest_columns:
            st.plotly_chart(interest_chart(frame, interest_columns), width="stretch", key="juros_plot")
        else:
            st.info("Selecione uma curva na barra lateral para exibir este gráfico.")
        st.subheader("O dólar ao longo do período")
        st.caption(
            f"Fechamento, média mensal e média móvel de {window} meses. Linha horizontal: média fixa dos 60 fechamentos de 2019–2023."
        )
        st.plotly_chart(
            exchange_chart(frame, window, historical_exchange_mean(loaded.frame)),
            width="stretch",
            key="dolar_plot",
        )
        if len(frame) < window:
            st.caption(
                "O recorte é menor que a janela escolhida; a média móvel ainda não possui observações suficientes."
            )
    with activity:
        st.subheader("Atividade econômica")
        st.caption("IBC-Br com ajuste sazonal (SGS 24364).")
        st.plotly_chart(activity_chart(frame, normalized), width="stretch", key="ibc_plot")
        st.subheader("Inflação mês a mês")
        st.plotly_chart(inflation_chart(frame), width="stretch", key="ipca_plot")
    with relations:
        left, right = st.columns(2)
        with left:
            st.subheader("Câmbio × inflação")
            st.caption("PTAX × IPCA 12 meses. Cor indica o ano; tamanho indica a meta Selic.")
            st.plotly_chart(scatter_chart(frame), width="stretch", key="scatter_plot")
        with right:
            st.subheader("Mapa de correlações")
            st.caption("Variações mensais" if changes else "Níveis das séries · atenção a tendências comuns")
            corr_data = correlation_input(loaded.frame, changes)
            corr_data = corr_data.loc[corr_data["data"].isin(frame["data"])]
            figure = heatmap_chart(corr_data, changes)
            if figure is None:
                st.info(
                    "Selecione mais competências: são necessárias duas séries não constantes e três pares válidos."
                )
            else:
                st.plotly_chart(figure, width="stretch", key="heatmap_plot")
        st.caption(
            "Associações contemporâneas; estes gráficos não identificam causalidade nem o efeito de defasagens."
        )
    with dataset:
        st.subheader("Dados do recorte")
        st.caption(
            "CSV com separador ponto e vírgula, vírgula decimal e UTF-8 BOM, adequado ao Excel em português."
        )
        st.download_button(
            "Baixar base filtrada (CSV)",
            data=export_csv(frame),
            file_name=f"bacen_{frame['data'].min():%Y%m}_{frame['data'].max():%Y%m}.csv",
            mime="text/csv",
            key="download_csv",
        )
        st.dataframe(
            frame.rename(columns=LABELS),
            hide_index=True,
            width="stretch",
            column_config={"data": st.column_config.DateColumn("Competência", format="MM/YYYY")},
        )
        st.caption(
            "A variação mensal do IBC-Br de janeiro/2019 fica vazia por não haver dezembro/2018 na base final."
        )
    with methods:
        methodology()
        if METADATA_PATH.exists():
            try:
                metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
                with st.expander("Proveniência do snapshot CSV local"):
                    st.caption(
                        "Estas informações descrevem o arquivo local, inclusive quando a fonte ativa é PostgreSQL."
                    )
                    st.json(metadata)
            except (OSError, ValueError):
                logger.warning("Metadados locais indisponíveis.")
    with answers:
        draw_answers(loaded.frame, frame, changes)
    st.divider()
    st.caption("BACEN / SGS · Projeto Final de Analytics Financeiro · Série histórica 2019–2023")


if __name__ == "__main__":
    main()
