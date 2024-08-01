# myeia

[![PyPI version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&ts=1683906897&type=6e&v=0.4.1&x2=0)](https://badge.fury.io/py/myeia)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://github.com/philsv/myeia/blob/main/LICENSE)
[![Weekly Downloads](https://static.pepy.tech/personalized-badge/myeia?period=week&units=international_system&left_color=grey&right_color=blue&left_text=downloads/week)](https://pepy.tech/project/myeia)
[![Monthly Downloads](https://static.pepy.tech/personalized-badge/myeia?period=month&units=international_system&left_color=grey&right_color=blue&left_text=downloads/month)](https://pepy.tech/project/myeia)
[![Downloads](https://static.pepy.tech/personalized-badge/myeia?period=total&units=international_system&left_color=grey&right_color=blue&left_text=downloads)](https://pepy.tech/project/myeia)

myeia is a simple Python wrapper for the U.S. Energy Information Administration (EIA) APIv2. It is designed to be simple to use and to provide a consistent interface for accessing EIA data.

## Installation

```ini
pip install myeia
```

## Requirements

* backoff
* pandas
* python-dateutil
* python-dotenv
* requests

## eia OPEN DATA Registration

To obtain an API Key you need to register on the [EIA website](https://www.eia.gov/opendata/register.php).

## eia API Query Browser

To find all EIA Datasets visit [API Dashboard](https://www.eia.gov/opendata/browser/).

## How to use

```python
from myeia.api import API

eia = API()
```

## Environment Variables

```bash
# Create your the .env file in your projects root directory
touch .env
```

By Default the EIA class will look for your API `EIA_TOKEN`.

If you have registered for an API key you can set it in your `.env` file.

```ini
EIA_TOKEN=YOUR_TOKEN_HERE
```

## Get Series

Lets look at an example of how to get the *EIA Natural Gas Futures*.
You can use the simpler v1 API method where you only need to pass the `series_id` or you can use the newer v2 API method where you need to pass the `route`, `series`, and `frequency`.

```python
df = eia.get_series(series_id="NG.RNGC1.D")

df = eia.get_series_via_route(
    route="natural-gas/pri/fut",
    series="RNGC1",
    frequency="daily",
)

df.head()
```

Output Example:

```ini
            Natural Gas Futures Contract 1 (Dollars per Million Btu)
Date
2022-09-13                                              8.284
2022-09-12                                              8.249
2022-09-09                                              7.996
2022-09-08                                              7.915
2022-09-07                                              7.842
...                                                       ...
```

## Different Facets

Lets look at another example the *Total OPEC Petroleum Supply* where the facet is available as `seriesId`. By Default it is set as `series` but we can define the facet as `seriesId`.

```python
df = eia.get_series(series_id="STEO.PAPR_OPEC.M")

df = eia.get_series_via_route(
    route="steo",
    series="PAPR_OPEC",
    frequency="monthly",
    facet="seriesId",
)

df.head()
```

 Output Example:

```ini
            Total OPEC Petroleum Supply
Date
2023-12-01                    34.517314
2023-11-01                    34.440397
2023-10-01                    34.376971
2023-09-01                    34.416242
2023-08-01                    34.451823
...                                 ...
```

## Filter by multiple facets

You can also filter by multiple facets. Lets look at the *UAE Crude oil, NGPL, and other liquids* where the facets we choose are `countryRegionId` and `productId`.
The difference here is that both facet columns are present in the dataframe, unlike the previous examples where only one facet was present.

```python
df = eia.get_series_via_route(
    route="international",
    series=["ARE", 55],
    frequency="monthly",
    facet=["countryRegionId", "productId"],
)

df.head()
```

Output Example:

```ini
           countryRegionId productId  Crude oil, NGPL, and other liquids
Date                                                                    
2024-03-01             ARE        55                         4132.394334
2024-02-01             ARE        55                         4132.394334
2024-01-01             ARE        55                         4142.394334
2023-12-01             ARE        55                         4082.394334
2023-11-01             ARE        55                         4082.394334
...                    ...       ...                                 ...
```

## Get Multiple Series

For multiple series you have to loop through the series and append the data to a list.

```python
data = []
for item in ["RNGC1", "RNGC2"]:
    df = eia.get_series_via_route(
    route="natural-gas/pri/fut",
    series=item,
    frequency="daily",
    facet="series",
    )
    data.append(df)

df = pd.concat(data, axis=1)
df.head()
```

Output Example:

```ini
            Natural Gas Futures Contract 1 (Dollars per Million Btu)  Natural Gas Futures Contract 2 (Dollars per Million Btu)
Date                                                                                                                          
2023-08-29                                              2.556                                                     2.662       
2023-08-28                                              2.579                                                     2.665       
2023-08-25                                              2.540                                                     2.657       
2023-08-24                                              2.519                                                     2.636       
2023-08-23                                              2.497                                                     2.592       
...                                                       ...                                                       ...
```

## Define a Start and End Date

You can define a start and end date for your query.

```python
df = eia.get_series(
    series_id="NG.RNGC1.D",
    start_date="2021-01-01",
    end_date="2021-01-31",
)

df.head()
```

Output Example:

```ini
            Natural Gas Futures Contract 1 (Dollars per Million Btu)
Date                                                                
2021-01-29                                              2.564       
2021-01-28                                              2.664       
2021-01-27                                              2.760       
2021-01-26                                              2.656       
2021-01-25                                              2.602       
...                                                       ...       
```

This also works for the `get_series_via_route` method.

```python
df = eia.get_series_via_route(
    route="natural-gas/pri/fut",
    series="RNGC1",
    frequency="daily",
    start_date="2021-01-01",
    end_date="2021-01-31",
)

df.head()
```

Output Example:

```ini
            Natural Gas Futures Contract 1 (Dollars per Million Btu)
Date
2021-01-29                                              2.564
2021-01-28                                              2.664
2021-01-27                                              2.760
2021-01-26                                              2.656
2021-01-25                                              2.602
...                                                       ...
```
