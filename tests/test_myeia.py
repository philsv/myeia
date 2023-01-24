import pandas as pd

from myeia.api import API


def test_get_data():
    eia = API()
    df = eia.get_data(route="natural-gas/pri/fut", series="RNGC1", frequency="daily")
    assert isinstance(df, pd.DataFrame)
