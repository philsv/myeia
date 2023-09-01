import os
import warnings
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

try:
    from pandas.errors import SettingWithCopyWarning
except ImportError as e:
    raise ImportError("Please upgrade your version of pandas to 1.5.3 or higher.") from e

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

load_dotenv()


def get_json_response(url: str, headers: dict) -> pd.DataFrame:
    """
    Helper function to get JSON response from API.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    json_response = response.json()
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
    start_date: str | None,
    end_date: str | None,
) -> tuple[str, str]:
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
        new_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the simpler APIv1 format.

        Args:
            series_id (str): The series ID.
            new_name (str, optional): A name you want to give the value column.
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

        if not new_name:
            series_description = base_df["series-description"][0] if "series-description" in base_df.columns else series_id
        else:
            series_description = new_name

        df = base_df[["period", "value"]]  # Keep only the date and value columns
        df.rename(columns={df.columns[0]: "Date", df.columns[1]: series_description}, inplace=True)
        df = format_time_series_data(df)

        start_date, end_date = get_date_range(start_date, end_date)
        return df.loc[start_date:end_date]  # type: ignore       
    

    def get_series_via_route(
        self,
        route: str,
        series: str | list[str],
        frequency: str,
        facet: str | None = None,
        new_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the newer APIv2 format.

        Args:
            route (str): The route to the series.
            series (str, list[str]): List of series ID's or a single series ID.
            frequency (str): The frequency of the series.
            facet (str, optional): The facet of the series. Defaults to "series".
            new_name (str, optional): A name you want to give the value column.
            start_date (str, optional): The start date of the series.
            end_date (str, optional): The end date of the series.

        Returns:
            pd.DataFrame: A DataFrame with the date and value columns.

        Examples:
            >>> eia = API()
            >>> eia.get_series_via_route("natural-gas/pri/fut", "RNGC1", "daily", "series")
            >>> eia.get_series_via_route("natural-gas/pri/fut", ["RNGC1", "RNGC2"], "daily", "series")
        """
        start_date, end_date = get_date_range(start_date, end_date)

        list_of_series = [series] if isinstance(series, str) else series
        
        data = []
        sort_args = "&sort[0][column]=period&sort[0][direction]=desc"

        for series in list_of_series:
            api_endpoint = f"{route}/data/?api_key={self.token}&data[]=value&frequency={frequency}&start={start_date}&end={end_date}"
            facet_args = f"&facets[{facet}][]={series}"
            url = f"{self.base_url}{api_endpoint}{facet_args}{sort_args}"
            base_df = get_json_response(url, headers=self.header)

            if not facet:
                facet = "series"

            if not new_name:
                new_name = ""

            if facet == "series":
                df = base_df[["period", "value", "series-description", "series"]]
            elif facet == "seriesId":
                df = base_df[["period", "value", "seriesDescription", "seriesId"]]

            df.reset_index(drop=True, inplace=True)
            name = new_name if new_name != "" else df[df.columns[2]][0]
            df.rename(columns={df.columns[1]: name}, inplace=True)
            df = df.iloc[:, :2]  # Keep only the date and value columns
            df.rename(columns={df.columns[0]: "Date"}, inplace=True)
            df = format_time_series_data(df)
            data.append(df)

        df = pd.concat(data, axis=1)
        df.sort_index(inplace=True, ascending=False)
        return df
