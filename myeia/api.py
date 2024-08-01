import logging
import os
import time
from datetime import date
from typing import Optional, Union

import backoff
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)

load_dotenv()


class API:
    """
    Python Wrapper for U.S. Energy Information Administration (EIA) APIv2.

    Documentation:
        https://www.eia.gov/opendata/documentation.php
    """

    def __init__(
        self,
        token: Optional[str] = None,
    ):
        self.token = token if token else os.getenv("EIA_TOKEN")
        self.base_url = "https://api.eia.gov/v2/"
        self.header = {"Accept": "*/*"}

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.HTTPError,
        max_tries=10,
        raise_on_giveup=True,
        jitter=backoff.full_jitter,
    )
    def get_response(
        self,
        url: str,
        headers: dict,
    ) -> pd.DataFrame:
        """
        Helper function to get the response from the EIA API and return it as a dataframe.
        """
        time.sleep(0.25)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return pd.DataFrame(json_response["response"]["data"])

    def format_date(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Helper function to format date.
        """
        if "period" in df.columns:
            df = df.rename(columns={"period": "Date"})
            df = df.set_index("Date")

            # If the index is only yearly, add month and day
            if len(str(df.index[0])) == 4:
                df.index = pd.to_datetime(df.index.astype(str) + "-01-01")

            df.index = pd.to_datetime(df.index)
        return df

    def get_series(
        self,
        series_id: str,
        data_identifier: str = "value",
        start_date: str = str(date.today() - relativedelta(months=840)),
        end_date: str = str(date.today() - relativedelta(months=-60)),
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the simpler APIv1 format.

        Args:
            series_id (str): The series ID.
            
            data_identifier (str, optional): The data identifier. Defaults to "value".
            start_date (str, optional): The start date of the series.
            end_date (str, optional): The end date of the series.

        Examples:
            >>> eia = API()
            >>> eia.get_series("NG.RNGC1.W")
        """
        api_endpoint = f"seriesid/{series_id}?api_key={self.token}"

        if start_date and end_date:
            api_endpoint += f"&start={start_date}&end={end_date}"

        url = f"{self.base_url}{api_endpoint}"
        df = self.get_response(url, self.header)
        df = self.format_date(df)
        df = df.sort_index(ascending=False)
        df[data_identifier] = df[data_identifier].astype(float)
        
        for col in df.columns:
            if "name" in col.lower() or "description" in col.lower():
                df = df.rename(columns={data_identifier: df[col][0]})
                df = df[df[col][0]].to_frame()
        
        return df

    def get_series_via_route(
        self,
        route: str,
        series: Union[str, list],
        frequency: str,
        facet: Union[str, list] = "series",
        start_date: str = str(date.today() - relativedelta(months=15)),
        end_date: str = str(date.today() - relativedelta(months=-15)),
        data_identifier: Optional[str] = "value",
        offset: int = 0,
        limit: int = 5000,
    ) -> pd.DataFrame:
        """
        Returns data for a given series in the newer APIv2 format.

        Args:
            route (str): The route to the series.
            series (str, list): The series.
            frequency (str): The frequency of the series.
            
            facet (str, list, optional): The facet of the series. Defaults to "series".
            rename_to (str, optional): The rename of the series. Defaults to "value".
            start_date (str, optional): The start date of the series. Defaults to str(date.today() - relativedelta(months=2)).
            end_date (str, optional): The end date of the series. Defaults to str(date.today() - relativedelta(months=-1)).
            data_identifier (str, optional): The data identifier of the series. Defaults to "value".
            offset (int, optional): The offset of the series. Defaults to 0.
            limit (int, optional): The limit of the series. Defaults to 5000.

        Examples:
            >>> eia = API()
            >>> eia.get_series_via_route("natural-gas/pri/fut", "RNGC1", "daily", rename_to="Natural Gas Futures Contract 1 (Dollars per Million Btu) (RNGC1)")
            >>> eia.get_series_via_route("natural-gas/pri/fut", ["RNGC1", "RNGC2"], "daily", facet=["series", "series"])
        """
        base_api_endpoint = f"{route}/data/?api_key={self.token}&frequency={frequency}&data[]={data_identifier}"

        if start_date and end_date:
            base_api_endpoint += f"&start={start_date}&end={end_date}"
            
        # Filter by multiple facets
        if isinstance(facet, list) and isinstance(series, list):
            for f, s in zip(facet, series):
                base_api_endpoint += f"&facets[{f}][]={s}"
        # Filter by single facet
        elif isinstance(facet, str) and isinstance(series, str):
            base_api_endpoint += f"&facets[{facet}][]={series}"
        else:
            raise ValueError(
                f"Ensure that facet and series are of the same type (either str or list). Received facet: {facet} and series: {series}."
            )

        api_endpoint = base_api_endpoint + f"&sort[0][column]=period&sort[0][direction]=desc&offset={offset}&length={limit}"
        url = f"{self.base_url}{api_endpoint}"

        df = self.get_response(url, self.header)

        if df.empty:
            raise ValueError(
                f"Error getting data for series: {series}. Please check your request."
            )

        df = self.format_date(df)
        df = df.sort_index(ascending=False)
        df[data_identifier] = df[data_identifier].astype(float)
        
        if isinstance(facet, str) and isinstance(series, str):
            for col in df.columns:
                if "name" in col.lower() or "description" in col.lower():
                    df = df.rename(columns={data_identifier: df[col][0]})
                    df = df[df[col][0]].to_frame()
                    break
        elif isinstance(facet, list) and isinstance(series, list):
            for col in df.columns:
                if "name" in col.lower() or "description" in col.lower():
                    df = df.rename(columns={data_identifier: df[col][0]})
                    facet.append(df[col][0])
                    df = df[facet]
                    break
 
        return df
