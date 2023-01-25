import pandas as pd
import pytest

from myeia.api import API


@pytest.mark.parametrize("route,series,frequency,facet", [("natural-gas/pri/fut", "RNGC1", "daily", "series"), ("petroleum/move/pipe", "MD0MP_R10-R20_1", "monthly", "series")])
def test_get_data(route, series, frequency, facet):
    eia = API()
    df = eia.get_data(route, series, frequency, facet)
    assert isinstance(df, pd.DataFrame)
