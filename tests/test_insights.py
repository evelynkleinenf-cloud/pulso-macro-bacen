"""Regressões para calendário, definição estatística e grade oficial da Linha 3."""

import numpy as np
import pandas as pd
import pytest

from src.charts import exchange_chart, interest_chart, scatter_chart
from src.insights import (
    above_average_windows,
    historical_exchange_mean,
    lagged_inflation,
    policy_windows,
    ranked_correlations,
)


@pytest.fixture
def frame():
    return pd.read_csv("data/macro_mensal.csv", parse_dates=["data"])


def test_reference_is_full_quinquennium_and_windows_do_not_bridge_omitted_months(frame):
    reference = historical_exchange_mean(frame)
    selected = frame.loc[frame.data.isin(pd.to_datetime(["2020-03-31", "2020-05-31"]))]
    windows = above_average_windows(frame, selected)
    assert reference == pytest.approx(4.943411666666667)
    assert len(windows) == 2
    assert windows.meses.tolist() == [1, 1]
    figure = exchange_chart(selected, 3, reference)
    assert figure.layout.shapes[0].y0 == reference
    assert figure.layout.shapes[0].y1 == reference


def test_future_inflation_is_aligned_by_calendar_and_excludes_unselected_outcomes():
    rng = np.random.default_rng(314)
    changes = rng.normal(0, 2, 60)
    dates = pd.date_range("2019-01-31", periods=60, freq="ME")
    data = pd.DataFrame(
        {"data": dates, "dolar": 5 * np.cumprod(1 + changes / 100), "ipca_mensal": np.r_[0, changes[:-1] * 2]}
    )
    full = lagged_inflation(data, data)
    assert full.loc[full.defasagem_meses == 1, "pearson"].iloc[0] == pytest.approx(1)
    assert full.loc[full.defasagem_meses == 1, "pares"].iloc[0] == 58
    selected = data.loc[data.data.dt.year.isin([2019, 2021])]
    separate = lagged_inflation(data, selected)
    assert separate.loc[separate.defasagem_meses == 1, "pares"].iloc[0] == 21
    assert separate.loc[separate.defasagem_meses == 1, "pearson"].iloc[0] == pytest.approx(1)
    assert lagged_inflation(data, data.iloc[:4]).pearson.isna().all()


def test_constant_lagged_series_has_no_spurious_correlation(frame):
    data = frame.assign(ipca_mensal=1.0)
    assert lagged_inflation(data, data).pearson.isna().all()


def test_policy_phase_uses_history_and_preceding_activity_baseline():
    data = pd.DataFrame(
        {
            "data": pd.date_range("2020-01-31", periods=6, freq="ME"),
            "selic": [5, 4, 4, 6, 6, 5],
            "ibc_br": [100, 90, 99, 100, 110, 105],
        }
    )
    result = policy_windows(data, data.iloc[3:5])
    assert len(result) == 1
    assert result.iloc[0].ciclo == "Alta"
    assert result.iloc[0].selic_inicial == 4
    assert result.iloc[0].variacao_ibc_pct == pytest.approx((110 / 99 - 1) * 100)
    assert result.iloc[0].base_ibc == pd.Timestamp("2020-03-31")
    split = policy_windows(data, data.iloc[[1, 3]])
    assert len(split) == 2


def test_ranking_has_unique_pairs_and_retains_negative_sign(frame):
    ranking = ranked_correlations(frame, frame, True)
    assert len(ranking) == 10
    assert ranking.pearson.abs().is_monotonic_decreasing
    assert (ranking.pearson < 0).any()
    assert all(left != right for left, right in zip(ranking.variavel_1, ranking.variavel_2))
    assert ranked_correlations(frame, frame.iloc[:1], True).empty


def test_official_combined_chart_and_bubble_axes(frame):
    combined = interest_chart(frame, ("selic", "ipca_12m", "juro_real_ex_post"))
    assert sorted(trace.type for trace in combined.data) == ["bar", "scatter", "scatter"]
    bubble = scatter_chart(frame)
    for year, trace in zip(sorted(frame.data.dt.year.unique()), bubble.data):
        selected = frame.loc[frame.data.dt.year == year]
        np.testing.assert_allclose(trace.y, selected.ipca_12m)
        np.testing.assert_allclose(trace.marker.size, selected.selic)
