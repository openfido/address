"""Address resolution pipeline

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

"""

version = 1 # specify API version

import sys, os
import json, csv
import pandas as pd
from shapely.geometry import Point
from geopandas.tools import geocode, reverse_geocode

#
# Defaults
#
default_options = {
    "reverse" : False,
}

default_config = {
    "provider" : "nominatim",
    "user_agent" : "csv_user_ht",
    "timeout" : 5,
    "retries" : 5,
    "sleep" : 1,
}

#
# Implementation of address package
#
def apply(data, options=default_options, config=default_config, warning=print):
    """Perform conversion between latitude,longitude and address

    ARGUMENTS:

        data (pandas.DataFrame)

            The data frame must contain either an `address` field or `latitude` and `longitude`
            fields, according to whether `options["reverse"]` is `True` or `False`.

        options (dict)

            "reverse" (bool) specifies the direction of resolution. Forward resolves `address`
            from `latitude,longitude` from . Reverse resolves `latitude,longitude`
            `address` from. The default is `options["reverse"] = False`, which provides
            forward resolution.

        config (dict)

            "provider" (str) specifies the providers of the address resolution algorithm.
            The default is "nominatim".

            "user_agent" (str) specifies the user agent for the address resolution algorithm.
            The default is "csv_user_ht".

    RETURNS:

        pandas.DataFrame

            The first (and only) return value is the `data` data frame with either the
            `address` or `latitude,longitude` fields updated/added.

    """

    if options["reverse"]:

        # convert address to lat,lon
        if not "address" in list(data.columns):
            raise Exception("reserve address resolution requires 'address' field")
        data.reset_index(inplace=True) # index is not meaningful
        for retries in range(config["retries"]):
            try:
                pos = geocode(data["address"],
                        provider = config["provider"],
                        user_agent = config["user_agent"],
                        timeout = config["timeout"],
                        )
                break
            except Exception as err:
                pos = err
            import time
            time.sleep(config["sleep"])
        if type(pos) is Exception:
            raise pos
        data["longitude"] = list(map(lambda p: p.x,pos["geometry"]))
        data["latitude"] = list(map(lambda p: p.y,pos["geometry"]))
        return data

    else:

        # convert lat,lon to address
        try:
            lats = list(map(lambda x: float(x),data["latitude"]))
            lons = list(map(lambda x: float(x),data["longitude"]))
            pos = list(map(lambda xy: Point(xy),list(zip(lons,lats))))
        except:
            pos = None
        if type(pos) == type(None):
            raise Exception("address resolution requires 'latitude' and 'longitude' fields")
        for retries in range(config["retries"]):
            try:
                addr = reverse_geocode(pos,
                        provider = config["provider"],
                        user_agent = config["user_agent"],
                        timeout = config["timeout"],
                        )
                break
            except Exception as err:
                addr = err
            import time
            time.sleep(config["sleep"])
        if type(addr) is Exception:
            raise addr
        data["address"] = pd.Series(addr["address"],dtype="string").tolist()
        return data

try:

    DATA = None
    CONFIG = default_config
    OPTIONS = default_options
    OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")
    OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")
    warnings = []
    with open(f"{OPENFIDO_INPUT}/config.csv","r") as cfg:
        reader = csv.reader(cfg)
        def cast(x,astype):
            if astype is bool:
                try:
                    return int(x)
                except:
                    if x.lower() in ("yes","true","no","false"):
                        return x.lower() in ("yes","true")
                    raise
            else:
                return astype(x)
        for row in reader:
            row0 = row[0].lower()
            if row0 == "data":
                DATA = pd.read_csv(f"{OPENFIDO_INPUT}/{row[1]}")
            elif row0 in CONFIG.keys():
                print("CONFIG",CONFIG)
                if len(row) == 1:
                    CONFIG[row0] = True
                else:
                    CONFIG[row0] = cast(row[1],type(CONFIG[row0]))
            elif row0 in OPTIONS.keys():
                if len(row) == 1:
                    OPTIONS[row0] = True
                else:   
                    OPTIONS[row0] = cast(row[1],type(CONFIG[row0]))
            else:
                print(f"WARNING [address]: config.csv parameter {row[0]} is not valid",file=sys.stderr)
        result = apply(DATA,OPTIONS,CONFIG,warning=lambda x: warnings.append(x))
        result.to_csv(f"{OPENFIDO_OUTPUT}/address.csv")
    exit(0)

except Exception as err:

    print(f"ERROR [address]: address resolution failed",file=sys.stderr)
    raise
