"""Configuração pública. Todos os caminhos são relativos à raiz do projeto."""

from datetime import date
from pathlib import Path

START_DATE = date(2019, 1, 1)
END_DATE = date(2023, 12, 31)
# Histórico auxiliar para o cálculo retrospectivo dos juros em 2019.
FETCH_START_DATE = date(2017, 12, 1)
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
CSV_PATH = DATA_DIR / "macro_mensal.csv"
METADATA_PATH = DATA_DIR / "metadata.json"
TABLE_NAME = "indicadores_macro"
API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

SERIES = {
    "selic": {"code": 432, "label": "Meta Selic", "unit": "% a.a.", "frequency": "diária"},
    "ipca_mensal": {"code": 433, "label": "IPCA mensal", "unit": "% a.m.", "frequency": "mensal"},
    "ipca_12m": {"code": 13522, "label": "IPCA em 12 meses", "unit": "%", "frequency": "mensal"},
    "dolar": {"code": 1, "label": "Dólar PTAX venda", "unit": "R$/US$", "frequency": "diária"},
    "ibc_br": {
        "code": 24364,
        "label": "IBC-Br com ajuste sazonal",
        "unit": "índice SGS",
        "frequency": "mensal",
    },
}

BASE_COLUMNS = ["selic", "ipca_mensal", "ipca_12m", "dolar", "dolar_media", "ibc_br", "selic_acumulada_12m"]
DERIVED_COLUMNS = ["juro_real_ex_post", "ibc_br_variacao_mensal"]
VALUE_COLUMNS = BASE_COLUMNS + DERIVED_COLUMNS

LABELS = {
    "selic": "Meta Selic (% a.a.)",
    "ipca_mensal": "IPCA mensal (% a.m.)",
    "ipca_12m": "IPCA em 12 meses (%)",
    "dolar": "Dólar PTAX (R$/US$)",
    "dolar_media": "PTAX média mensal (R$/US$)",
    "ibc_br": "IBC-Br com ajuste sazonal (índice SGS)",
    "selic_acumulada_12m": "Selic acumulada em 12 meses — proxy (%)",
    "juro_real_ex_post": "Juro real ex-post — proxy (% em 12 meses)",
    "ibc_br_variacao_mensal": "Variação mensal do IBC-Br (%)",
}
