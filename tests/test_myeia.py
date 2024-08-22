import pandas as pd
import pytest

from myeia.api import API

eia = API()


@pytest.mark.parametrize(
    "series_id, start_date, end_date",
    [
        ("NG.RNGC1.D", "2024-01-01", "2024-02-01"),
        ("PET.WCESTUS1.W", "2024-01-01", "2024-02-01"),
        ("INTL.29-12-HKG-BKWH.A", "2024-01-01", "2024-02-01"),
        ("STEO.PATC_WORLD.M", "2024-01-01", "2024-02-01"),
    ],
)
def test_get_series(series_id, start_date, end_date):
    """Test get_series method."""
    df = eia.get_series(series_id, start_date=start_date, end_date=end_date)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "route, series, frequency, facet",
    [
        ("steo", "PADI_OPEC", "monthly", "seriesId"),
        ("natural-gas/pri/fut", "RNGC1", "daily", "series"),
        ("petroleum/stoc/wstk", "WCESTUS1", "weekly", "series"),
        ("petroleum/move/pipe", "MD0MP_R10-R20_1", "monthly", "series"),
        ("total-energy", "PATWPUS", "monthly", "msn"),
        ("international", ["ARE", 55], "monthly", ["countryRegionId", "productId"]),
    ],
)
def test_get_series_via_route(route, series, frequency, facet):
    """Test get_series_via_route method."""
    df = eia.get_series_via_route(route, series, frequency, facet)
    assert isinstance(df, pd.DataFrame)
