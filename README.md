[![validation](https://github.com/openfido/address/actions/workflows/main.yml/badge.svg)](https://github.com/openfido/address/actions/workflows/main.yml)

The address resolution pipeline resolves addresses and locations.

CONFIG
------

The following parameters are recognized in `config.csv`:

* DATA: The CSV data file name contain address or location (required)

* REVERSE: Boolean value indicating whether the data contains locations
  (False, default) or addresses (True)

* PROVIDER: Resolver provider (default is "nominatim")

* USER_AGENT: Resolver user agent (default is "csv_user_ht")

* TIMEOUT: Resolver timeout in seconds (default is 5)

* RETRIES: Resolver retry limit (default is 5)

* SLEEP: Resolver sleep between retries in seconds (default 1)

INPUT
-----

The format of the input depends on the value of REVERSE in config.csv.

* REVERSE=False

The CSV file must include a *latitude* and *longitude* column.

* REVERSE=True

The CSV file must include an *address* column.

OUTPUT
------

The format of the output depends on the value of REVERSE in config.csv.

* REVERSE=False

The CSV file will include an *address* column.

* REVERSE=True

The CSV file will include a *latitude* and *longitude* column.
