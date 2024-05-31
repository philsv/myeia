import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Tuple, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import JSONDecodeError

try:
    from pandas.errors import SettingWithCopyWarning
except ImportError as e:
    raise ImportError("Please upgrade your version of pandas to 1.5.3 or higher.") from e

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)



def get_json_response(url: str, headers: dict) -> pd.DataFrame:
    """
    Helper function to get JSON response from API.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    try:
        json_response = response.json()
    except JSONDecodeError as e:
        logging.error(f"Response: {response.text}")
        raise ValueError(f"Error decoding JSON response ({e}). Data might be incomplete or missing. Chunking your request might help.") from e
    return pd.DataFrame(json_response["response"]["data"])


def format_time_series_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to format time series data.
    """
    df.set_index("Date", inplace=True)

    # If the index is only a year, add month and day
    if len(str(df.index[0])) == 4:
        df.index = pd.to_datetime(df.index.astype(str) + "-01-01")

    df.index = pd.to_datetime(df.index)
    return df


def get_date_range(
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
) -> Tuple[str, str]:
    """
    Helper function to get the start and end date for a given series.
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365 * 60)).strftime("%Y-%m-%d")

    if not end_date:
        end_date = (datetime.now() + timedelta(days=365 * 50)).strftime("%Y-%m-%d")
    return start_date, end_date


@dataclass
class API:
    """
    Python Wrapper for U.S. Energy Information Administration (EIA) APIv2.

    Documentation:
        https://www.eia.gov/opendata/documentation.php
    """

    token: Optional[str] = os.getenv("EIA_TOKEN")  # Get API token from .env file
    base_url: str = "https://api.eia.gov/v2/"
    header: dict = field(default_factory=lambda: {"Accept": "*/*"})

    def get_series(
        self,
        series_id: str,
        start_date: Union[str, None] = None,
        end_date: Union[str, None] = None,
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the simpler APIv1 format.

        Args:
            series_id (str): The series ID.
            start_date (str, optional): The start date of the series.
            end_date (str, optional): The end date of the series.

        Returns:
            pd.DataFrame: A DataFrame with the date and value columns.

        Examples:
            >>> eia = API()
            >>> eia.get_series("NG.RNGC1.W")
        """
        api_endpoint = f"seriesid/{series_id}?api_key={self.token}"

        url = f"{self.base_url}{api_endpoint}"
        base_df = get_json_response(url, headers=self.header)
        series_description = base_df["series-description"][0] if "series-description" in base_df.columns else series_id

        df = base_df[["period", "value"]]  # Keep only the date and value columns
        df.rename(columns={df.columns[0]: "Date", df.columns[1]: series_description}, inplace=True)
        df = format_time_series_data(df)

        start_date, end_date = get_date_range(start_date, end_date)
        mask = (df.index >= start_date) & (df.index <= end_date)  # To avoid slicing errors (FutureWarning: slicing on non-monotonic DatetimeIndexes with non-existing keys)
        return df.loc[mask]

    def get_series_via_route(
        self,
        route: str,
        series: Union[str, List[str]],
        frequency: str,
        facet: Union[str, None] = None,
        start_date: Union[str, None] = None,
        end_date: Union[str, None] = None,
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the newer APIv2 format.

        Args:
            route (str): The route to the series.
            series (str, list[str]): List of series ID's or a single series ID.
            frequency (str): The frequency of the series.
            facet (str, optional): The facet of the series. Defaults to "series".
            start_date (str, optional): The start date of the series.
            end_date (str, optional): The end date of the series.

        Returns:
            pd.DataFrame: A DataFrame with the date and value columns.

        Examples:
            >>> eia = API()
            >>> eia.get_series_via_route("natural-gas/pri/fut", "RNGC1", "daily")
            >>> eia.get_series_via_route("natural-gas/pri/fut", ["RNGC1", "RNGC2"], "daily", "series")
        """
        start_date, end_date = get_date_range(start_date, end_date)

        list_of_series = [series] if isinstance(series, str) else series
        
        if not facet:
            facet = "series"

        data = []
        sort_args = "&sort[0][column]=period&sort[0][direction]=desc"

        for series in list_of_series:
            api_endpoint = f"{route}/data/?api_key={self.token}&data[]=value&frequency={frequency}&start={start_date}&end={end_date}"
            facet_args = f"&facets[{facet}][]={series}"
            url = f"{self.base_url}{api_endpoint}{facet_args}{sort_args}"
            base_df = get_json_response(url, headers=self.header)

            if base_df.empty:
                raise ValueError(f"Error getting data for series: {series}. Please check your request.")

            if facet == "series":
                df = base_df[["period", "value", "series-description", "series"]]
            else:
                df = base_df[["period", "value", "seriesDescription", facet]]

            df.reset_index(drop=True, inplace=True)
            df.rename(columns={df.columns[1]: df[df.columns[2]][0]}, inplace=True)
            df = df.iloc[:, :2]  # Keep only the date and value columns
            df.rename(columns={df.columns[0]: "Date"}, inplace=True)
            df = format_time_series_data(df)
            data.append(df)

        df = pd.concat(data, axis=1)
        df.sort_index(inplace=True, ascending=False)
        return df
