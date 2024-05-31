import pandas as pd
import pytest

from myeia.api import API

eia = API()


@pytest.mark.parametrize(
    "series_id,start_date,end_date",
    [
        ("NG.RNGC1.D", None, None),
        ("NG.RNGC1.D", "2021-01-01", "2021-01-31"),
        ("PET.WCESTUS1.W", None, None),
        ("PET.MD0MP_R10-R20_1.M", None, None),
        ("INTL.29-12-HKG-BKWH.A", None, None),
    ],
)
def test_get_series(series_id, start_date, end_date):
    df = eia.get_series(series_id, start_date=start_date, end_date=end_date)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "route,series,frequency,facet,start_date,end_date",
    [
        ("natural-gas/pri/fut", "RNGC1", "daily", "series", None, None),
        ("natural-gas/pri/fut", ["RNGC1", "RNGC2"], "daily", "series", None, None),
        ("natural-gas/pri/fut", ["RNGC1", "RNGC2"], "daily", "series", "2021-01-01", "2021-11-30"),
        ("petroleum/stoc/wstk", "WCESTUS1", "weekly", "series", None, None),
        ("petroleum/move/pipe", "MD0MP_R10-R20_1", "monthly", "series", None, None),
        ("petroleum/crd/crpdn", "MCRFPP51", "monthly", "series", None, None),
        ("petroleum/crd/crpdn", "MCRFPP52", "monthly", "series", None, None),
        ("petroleum/crd/crpdn", ["MCRFPP51", "MCRFPP52"], "monthly", "series", None, None),
        ("petroleum/crd/crpdn", ["MCRFPP51", "MCRFPP52"], "monthly", "series", "2021-01-01", "2021-11-31"),
        ("total-energy", "PATWPUS", "monthly", "msn", "2020-01-01", None),
    ],
)
def test_get_series_via_route(route, series, frequency, facet, start_date, end_date):
    df = eia.get_series_via_route(route, series, frequency, facet, start_date=start_date, end_date=end_date)
    assert isinstance(df, pd.DataFrame)
