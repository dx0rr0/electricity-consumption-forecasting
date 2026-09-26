# Data source and reconstruction

`clean_hourly_data.csv` is derived from **Individual Household Electric Power Consumption**, by Georges Hebrail and Alice Berard, UCI Machine Learning Repository, DOI [10.24432/C58K54](https://doi.org/10.24432/C58K54). The [UCI dataset page](https://archive.ics.uci.edu/dataset/235/individualhouseholdelectricpowerconsumption) provides the source ZIP and identifies its license as [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The same dataset has a [Kaggle mirror](https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set).

The source contains minute-averaged household active power readings (kW) from a home in Sceaux, France. The archived notebooks used an hourly target. To reproduce it, [`scripts/prepare_data.py`](../scripts/prepare_data.py) performs these transformations:

1. Parse `Date`, `Time`, and `Global_active_power` from the UCI ZIP.
2. Forward-fill missing minute power values.
3. Sum each hour and round to two decimals.
4. Remove the first and last partial hours.

The resulting 34,587 rows span **2006-12-16 18:00** through **2010-11-26 20:00**. The first and last values, row count, mean, standard deviation, minimum and maximum match saved outputs in the original notebooks. The original preprocessing source code was unavailable, so this is a strong reconstruction rather than a byte-for-byte comparison with the missing CSV.

`ds` is the hour timestamp. `y` is the sum of the minute-level kW readings; `y / 60` gives kWh for a complete hour. The file contains transformed data and is shared with attribution under the source dataset's CC BY 4.0 license. The raw UCI archive is not included.

**Caveat:** Forward filling across missing stretches assumes consumption stayed at the last observed level. This reproduces the archived target statistics but can bias affected hours. No timezone conversion was applied; timestamps follow the source file.
