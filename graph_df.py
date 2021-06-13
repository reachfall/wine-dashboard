# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd

# %%
df = pd.read_csv('data/wine_extended.csv', index_col=0)


# %%
# split data into 2 categories: reviews (current data) and wines (unique wines) 
reviews = df
wines = df.drop_duplicates(subset="title", keep="first")


# %%
# choropleth data
df_choropleth = wines.groupby(['country', 'continent'])['iso_a2'].value_counts().to_frame().rename(columns={"iso_a2":"no_wines"}).reset_index()


# %%
# sunburst data
df_sunburst = df_choropleth.copy()
df_sunburst["continent_class"] = df_sunburst["continent"].replace(
    {"Asia": "Other", "Oceania": "Other", "Africa": "Other"}
)


# %%
# treemap data
df_treemap = pd.merge(df_choropleth, df.groupby("country").mean().reset_index(), on="country")
df_treemap = df_treemap.query("no_wines>100")
df_treemap["world"] = "World"


# %%
# taster finder
def find_taster(name, twitter, name_col, twitter_col):
    return (name == name_col) & ((twitter == twitter_col) | ((twitter != twitter) & (twitter_col != twitter_col)))


# %%
df_all_tasters_details = (
    reviews.groupby(
        ["taster_name", "taster_twitter_handle", "country", "variety"], dropna=False
    )
    .agg({"variety": "count", "points": "mean", "price": "mean"})
    .rename(columns={"variety": "no_reviews", "points":"avg_points", "price":"avg_price"})
    .reset_index()
)


# %%
# get taster reviews details (by country or variety)
def get_taster_details(taster_name, taster_twitter_handle, by):
    return (
        df_all_tasters_details[
            find_taster(
                taster_name,
                taster_twitter_handle,
                df_all_tasters_details["taster_name"],
                df_all_tasters_details["taster_twitter_handle"],
            )
        ]
        .groupby([f"{by}"])
        .agg({"no_reviews": "sum", "avg_points": "mean", "avg_price": "mean"})
        .round({'avg_points': 2, 'avg_price':2})
        .dropna()
        .reset_index()
    )


# %%
# taster info data
df_tasters_stats = reviews.groupby(['taster_name', 'taster_twitter_handle'], dropna=False).agg({'variety':'count', 'points':['min', 'max', 'mean'], 'price':['min', 'max', 'mean']}).reset_index()
df_tasters_stats.columns = ['_'.join(col) for col in df_tasters_stats.columns.values]
df_tasters_stats.rename(columns={'taster_name_':'taster_name', 'taster_twitter_handle_':'taster_twitter_handle', 'variety_count':'no_reviews'}, inplace=True)


# %%
def get_taster_stats(taster_name, taster_twitter_handle):
    return df_tasters_stats[find_taster(taster_name, taster_twitter_handle, df_tasters_stats['taster_name'], df_tasters_stats['taster_twitter_handle'])]


# %%
# find wine reviews (only min max values)
def find_wine_review(taster_name, taster_handle, taster_stats, param):
    return reviews[find_taster(taster_name, taster_handle, reviews['taster_name'], reviews['taster_twitter_handle']) & (reviews[param.split('_')[0]] == taster_stats[param].values[0])].head(1)


