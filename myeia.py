import json
import urllib.request
from typing import Optional

import pandas as pd


class EIA(object):
    def __init__(
        self,
        key: Optional[str],
    ) -> None:
        self.key = key

    def search_by_category_id(
        self,
        category_id: str,
        series: bool = False,
    ) -> pd.DataFrame:
        """Returns a DataFrame of sub category names and IDs from a category ID.

        Args:
            category_id (str): A unique numerical ID of the category to fetch.
            series (bool, optional): True returns all related series IDs, names, frequencies, units and when it was last updated.
        """
        url = f"https://api.eia.gov/category/?api_key={self.key}&category_id={category_id}"

        with urllib.request.urlopen(url) as url:
            response = json.loads(url.read().decode())

        if series == False:
            df = pd.DataFrame(response["category"]["childcategories"])
            df.set_index("category_id", inplace=True)

        else:
            try:
                df = pd.DataFrame(response["category"]["childseries"])
                df.set_index("series_id", inplace=True)
            except (KeyError):
                print("No Series Found")
        return df

    def search_by_series_id(
        self,
        series_id: str,
    ) -> pd.DataFrame:
        """Returns a DataFrame of category names and IDs the series is a member of.

        Args:
            series_id (str): The series id (also called source key) is a case-insensitive string\
            consisting of letters, numbers, dashes ("-") and periods (".") that uniquely identifies an EIA series.
        """
        url = f"https://api.eia.gov/category/?api_key={self.key}&series_id={series_id}"

        with urllib.request.urlopen(url) as url:
            response = json.loads(url.read().decode())

        df = pd.DataFrame(response["category"]["childcategories"])
        df.set_index("category_id", inplace=True)
        return df

    def data_by_series_id(
        self,
        series_id: str,
    ) -> pd.DataFrame:
        """Returns the Timeseries Dataset as a DataFrame of a series ID."""

        url = f"https://api.eia.gov/series/?api_key={self.key}&series_id={series_id}"

        with urllib.request.urlopen(url) as url:

            try:
                response = json.loads(url.read().decode())
                df = pd.DataFrame(
                    response["series"][0]["data"],
                    columns=[
                        "Date",
                        response["series"][0]["name"],
                    ],
                )
                df["Date"] = pd.to_datetime(df["Date"])

            except (ValueError):
                df = pd.DataFrame(
                    response["series"][0]["data"],
                    columns=["Date", response["series"][0]["name"]],
                )
                df["Date"] = pd.to_datetime(df["Date"], format="%Y%m")

            df.set_index("Date", inplace=True)
        return df