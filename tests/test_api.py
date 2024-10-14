import json
import os

import pandas as pd
import pytest
import requests

from myeia import API

eia = API()


@pytest.mark.parametrize(
    "series_id, start_date, end_date",
    [
        ("NG.RNGC1.D", "2020-01-01", "2024-02-01"),
        ("PET.WCESTUS1.W", "2020-01-01", "2024-02-01"),
        ("INTL.29-12-HKG-BKWH.A", "2020-01-01", "2024-02-01"),
        ("STEO.PATC_WORLD.M", "2024-01-01", "2024-02-01"),
    ],
)
def test_get_series(series_id, start_date, end_date, mocker):
    """Test get_series method."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data/")
    file = series_id+"_"+start_date+"_"+end_date+".json"

    class MockGetResponse:
        def status_code(self):
            return 200

        def json(self):
            if os.path.isfile(os.path.join(data_dir, file)):
                with open(os.path.join(data_dir, file), "r") as mock_file:
                    return json.load(mock_file)
            else:
                raise FileNotFoundError("File not found")

        def raise_for_status(self):
            pass

    # if test data file exists, mock requests.get
    if os.path.isfile(os.path.join(data_dir, file)):
        mocker.patch("requests.get", return_value=MockGetResponse())

    # register spy on requests.get
    spy_get = mocker.spy(requests, "get")

    df = eia.get_series(series_id, start_date=start_date, end_date=end_date)

    # get the return value of the spy
    spy_return = spy_get.spy_return
    json_response = spy_return.json()
    # clean request data as it can contain secrets like api key
    json_response["request"] = {}

    # if test data file not exists, create it
    # then write mock data to it
    if not os.path.exists(data_dir):
        os.mkdir(os.path.dirname(data_dir))
    if not os.path.isfile(os.path.join(data_dir, file)):
        with open(os.path.join(data_dir, file), "w") as f:
            f.write(json.dumps(json_response))

    assert not df.empty
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
def test_get_series_via_route(route, series, frequency, facet, mocker):
    """Test get_series_via_route method."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data/")
    file = route.replace("/","-")+"_"+series+"_"+frequency+"_"+facet+".json"

    class MockGetResponse:
        def status_code(self):
            return 200

        def json(self):
            if os.path.isfile(os.path.join(data_dir, file)):
                with open(os.path.join(data_dir, file), "r") as mock_file:
                    return json.load(mock_file)
            else:
                raise FileNotFoundError("File not found")

        def raise_for_status(self):
            pass

    # if test data file exists, mock requests.get
    if os.path.isfile(os.path.join(data_dir, file)):
        mocker.patch("requests.get", return_value=MockGetResponse())

    # register spy on requests.get
    spy_get = mocker.spy(requests, "get")

    df = eia.get_series_via_route(route, series, frequency, facet)

    # get the return value of the spy
    spy_return = spy_get.spy_return
    json_response = spy_return.json()
    # clean request data as it can contain secrets like api key
    json_response["request"] = {}

    # if test data file not exists, create it
    # then write mock data to it
    if not os.path.exists(data_dir):
        os.mkdir(os.path.dirname(data_dir))
    if not os.path.isfile(os.path.join(data_dir, file)):
        with open(os.path.join(data_dir, file), "w") as f:
            f.write(json.dumps(json_response))

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
