import pandas as pd

import country_converter as coco
from pycountry_convert import country_alpha2_to_continent_code

# mapping continent codes to continents
continents = {
    "NA": "North America",
    "SA": "South America",
    "AS": "Asia",
    "OC": "Oceania",
    "AF": "Africa",
    "EU": "Europe",
}

# fetching data
df = pd.read_csv("data/wine.csv", index_col=0)
del df["description"]
df.dropna(subset=["country", "variety"], inplace=True)
df["taster_name"].fillna("Anonymous tasters", inplace=True)

df["country"].replace({'England':'United Kingdom'}, inplace=True)
df["iso_a2"] = coco.convert(names=df["country"], to="ISO2")
df["continent_code"] = df["iso_a2"].apply(
    lambda x: country_alpha2_to_continent_code(x)
)
df["continent"] = df["continent_code"].apply(lambda x: continents[x])
df.drop(columns=['continent_code'], inplace=True)

df.to_csv("wine_extended.csv")
