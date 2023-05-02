import os
import warnings
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

try:
    from pandas.errors import SettingWithCopyWarning
except ImportError as e:
    raise ImportError("Please upgrade your version of pandas to 1.5.3 or higher.") from e

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

load_dotenv()


@dataclass
class API:
    """
    Python Wrapper for U.S. Energy Information Administration (EIA) APIv2.
    """

    token: Optional[str] = os.getenv("EIA_TOKEN")
    url: str = "https://api.eia.gov/v2/"

    def get_series(
        self,
        series_id: str,
        new_name: str = "",
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the simpler APIv1 format.

        Args:
            series_id (str): The series ID. For example, "NG.RNGC1.W".
            new_name (str): A name you want to give the value column.

        Returns:
            pd.DataFrame: A DataFrame with the date and value columns.
        """
        headers = {"Accept": "*/*"}
        url = f"{self.url}seriesid/{series_id}?api_key={self.token}"
        base_df = self.get_json_response(url, headers)

        if not new_name:
            series_description = base_df["series-description"][0] if "series-description" in base_df.columns else series_id
        else:
            series_description = new_name

        df = base_df[["period", "value"]]

        df.rename(columns={df.columns[0]: "Date", df.columns[1]: series_description}, inplace=True)
        return self.format_time_series_data(df)

    def get_series_via_route(
        self,
        route: str,
        series: str,
        frequency: str,
        facet: str = "series",
        new_name: str = "",
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the newer APIv2 format.

        Args:
            route (str): The route to the series. For example, "natural-gas/pri/fut".
            series (str): The series ID. For example, "RNGC1".
            frequency (str): The frequency of the series. For example, "daily".
            facet (str): The facet of the series. For example, "series", "seriesId".
            new_name (str): A name you want to give the value column.

        Returns:
            pd.DataFrame: A DataFrame with the date and value columns.
        """
        headers = {"Accept": "*/*"}

        api_route = f"{route}/data/?api_key={self.token}&data[]=value&frequency={frequency}"
        series = f"&facets[{facet}][]={series}"
        sort = "&sort[0][column]=period&sort[0][direction]=desc"
        url = f"{self.url}{api_route}{series}{sort}"

        base_df = self.get_json_response(url, headers)

        if facet == "series":
            df = base_df[["period", "value", "series-description", "series"]]
        elif facet == "seriesId":
            df = base_df[["period", "value", "seriesDescription", "seriesId"]]

        df.reset_index(drop=True, inplace=True)

        name = new_name if new_name != "" else df[df.columns[2]][0]
        df.rename(columns={df.columns[1]: name}, inplace=True)
        df = df.iloc[:, :2]

        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        return self.format_time_series_data(df)

    def format_time_series_data(self, df):
        """
        Helper function to format time series data.
        """
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        return df

    def get_json_response(self, url: str, headers: dict):
        """
        Helper function to get JSON response from API.
        """
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return pd.DataFrame(json_response["response"]["data"])
