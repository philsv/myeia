import os
import warnings
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
load_dotenv()


@dataclass
class API:
    """
    Python Wrapper for U.S. Energy Information Administration (EIA) APIv2.
    """

    token: Optional[str] = os.getenv("EIA_TOKEN")
    url: str = "https://api.eia.gov/v2/"

    def get_data(
        self,
        route: str,
        series: str,
        frequency: str,
        facet: str = "series",
        new_name: str = "",
    ) -> pd.DataFrame:
        """
        Returns data for a given series.
        """

        headers = {
            "Accept": "*/*",
        }

        api_route = f"{route}/data/?api_key={self.token}&data[]=value&frequency={frequency}"

        series = f"&facets[{facet}][]={series}"

        sort = "&sort[0][column]=period&sort[0][direction]=desc"

        url = f"{self.url}{api_route}{series}{sort}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        base_df = pd.DataFrame(json_response["response"]["data"])

        if facet == "series":
            df = base_df[["period", "value", "series-description", "series"]]

        elif facet == "seriesId":
            df = base_df[["period", "value", "seriesDescription", "seriesId"]]

        df.reset_index(drop=True, inplace=True)

        name = df[df.columns[2]][0]

        if new_name != "":
            name = new_name

        df.rename(columns={df.columns[1]: name}, inplace=True)

        df = df.iloc[:, :2]

        df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        return df
