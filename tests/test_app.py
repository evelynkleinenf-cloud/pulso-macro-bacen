"""Testes de interação reais do Streamlit, sem navegador e sem credenciais."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(autouse=True)
def offline_database(monkeypatch):
    """Mantém o AppTest independente de segredos e serviços reais do desenvolvedor."""
    monkeypatch.setattr("src.database.read_database", Mock(side_effect=ConnectionError("offline")))


def open_app():
    app = AppTest.from_string(Path("app.py").read_text(encoding="utf-8"), default_timeout=30).run()
    assert not app.exception
    return app


def test_default_dashboard_has_metrics_tabs_and_six_charts():
    app = open_app()
    assert len(app.metric) == 4
    assert len(app.tabs) == 5
    assert len(app.get("plotly_chart")) == 6
    assert app.metric[0].value == "11,75%"
    assert len(app.get("download_button")) == 1


def test_year_filter_updates_table_and_reset_restores_defaults():
    app = open_app()
    app.multiselect(key="anos").set_value([2020]).run()
    assert not app.exception
    assert not app.warning
    # Primeira tabela é a base exportável; a segunda é o catálogo de séries.
    assert len(app.dataframe[0].value) == 12
    assert app.metric[0].value == "2,00%"
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 60
    assert app.multiselect(key="anos").value == [2019, 2020, 2021, 2022, 2023]


def test_empty_year_selection_can_be_reset():
    app = open_app()
    app.multiselect(key="anos").set_value([]).run()
    assert not app.exception
    assert len(app.metric) == 0
    app.button(key="reset_empty").click().run()
    assert not app.exception
    assert len(app.metric) == 4


def test_one_month_and_empty_curves_are_handled():
    app = open_app()
    options = app.select_slider(key="periodo").value
    app.select_slider(key="periodo").set_range(options[-1], options[-1]).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 1
    assert all(metric.delta == "" for metric in app.metric)
    assert len(app.get("plotly_chart")) == 5  # correlação não definida para um mês
    app.multiselect(key="juros").set_value([]).run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 4


def test_chart_controls_and_disjoint_years():
    app = open_app()
    app.multiselect(key="anos").set_value([2019, 2023]).run()
    app.selectbox(key="janela").select(12).run()
    app.toggle(key="normalizar").set_value(True).run()
    app.radio(key="correlacao").set_value("Níveis").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 24
    assert len(app.get("plotly_chart")) == 6
