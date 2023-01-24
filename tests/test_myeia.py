import pandas as pd

from src import myeia


def test_get_data():
    eia = myeia.API()
    df = eia.get_data(route="natural-gas/pri/fut", series="RNGC1", frequency="daily")
    assert isinstance(df, pd.DataFrame)