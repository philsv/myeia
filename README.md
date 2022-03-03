# myeia

**myeia** is a simple Python wrapper for the U.S. Energy Information Administration (EIA) API.

# Requirements

* pandas

# Installation

```
pip install myeia
```

#  eia OPEN DATA Registration

To obtain an API Key you need to register on the [EIA website](https://www.eia.gov/opendata/register.php).


# eia API Query Browser

To find all EIA Datasets visit [API Query Browser](https://www.eia.gov/opendata/qb.php)

# Authentication

```
import myeia

eia = myeia.EIA("API_KEY")
```

# Examples

* search_by_category_id will return all related sub categories.

```
eia.search_by_category_id("1")
```

* Optionally you can set series=True which will return series IDs from category.

```
eia.search_by_category_id("20", series=True)
```

* search_by_series_id will return category names and IDs a series is a member of.

```
eia.search_by_series_id("PET.RWTC.D")
```

* data_by_series_id will return a Timeseries Dataset from series ID.

```
eia.data_by_series_id("PET.RWTC.D")
```
