# myeia

myeia is a simple Python wrapper for the U.S. Energy Information Administration (EIA) APIv2. It is designed to be simple to use and to provide a consistent interface for accessing EIA data.

# Installation

```ini
pip install myeia
```

# Requirements

* pandas
* requests
* python-dotenv

#  eia OPEN DATA Registration

To obtain an API Key you need to register on the [EIA website](https://www.eia.gov/opendata/register.php).

# eia API Query Browser

To find all EIA Datasets visit [API Dashboard](https://www.eia.gov/opendata/browser/).

# How to use

```python
from myeia import API

eia = API()
```

By Default the EIA class will look for your API `EIA_TOKEN`. 

If you have registered for an API key you can set it in your `.env` file.


```ini
EIA_TOKEN=YOUR_TOKEN_HERE
```

Lets look at an example of how to get the *EIA Natural Gas Futures*.

```python
df = eia.get_data(
    route="natural-gas/pri/fut",
    series="RNGC1",
    frequency="daily",
)

df.head()
```

Output Example:
```
            Natural Gas Futures Contract 1 (Dollars per Million Btu)
Date
2022-09-13                                              8.284
2022-09-12                                              8.249
2022-09-09                                              7.996
2022-09-08                                              7.915
2022-09-07                                              7.842
...
```

Lets look at another example the *Total OPEC Petroleum Supply* where the facet is available as `seriesId`. By Default it is set as `series` but we can define the facet as `seriesId`.

```python
df = eia.get_data(
    route="steo",
    series="PAPR_OPEC",
    frequency="monthly",
    facet="seriesId",
)

df.head()
```

 Output Example:
```
            Total OPEC Petroleum Supply
Date
2023-12-01                    34.517314
2023-11-01                    34.440397
2023-10-01                    34.376971
2023-09-01                    34.416242
2023-08-01                    34.451823
```