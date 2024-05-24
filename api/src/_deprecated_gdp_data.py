import numpy as np
import math

def get_gdp_data():
    # Fetch CSV file (uploaded to Files tab)
    usd_gdp_per_capita_df = pd.read_csv("data/hex/Fair Water - NGDPDPC.csv")

    # Normalise names:
    usd_gdp_per_capita_df["country"] = usd_gdp_per_capita_df["country"].apply(
        lambda x: normalize_name(x)
    )

    # Merge with all_countries_in_the_world_df to get country ISO code
    usd_gdp_per_capita_df = usd_gdp_per_capita_df.merge(
        all_countries_in_the_world_df, left_on="country", right_on="name", how="left"
    )

    # Index by ISO (alpha_2) code:
    usd_gdp_per_capita_df.set_index("code", inplace=True)

    # Format and process year data
    FIRST_GDP_DATA_YEAR = 1980
    LAST_GDP_DATA_YEAR = 2029
    DESIRED_ACTUAL_GDP_DATA_YEAR = 2024
    years = list(map(str, range(FIRST_GDP_DATA_YEAR, DESIRED_ACTUAL_GDP_DATA_YEAR)))
    for year in years:
        usd_gdp_per_capita_df[year] = usd_gdp_per_capita_df[year].apply(
            lambda x: np.nan
            if x == "no data"
            else round(float(x))
            if pd.notnull(x)
            else np.nan
        )

    # Find the last year with GDP(actual, not forecast) data for each country
    usd_gdp_per_capita_df["last_year"] = usd_gdp_per_capita_df.apply(
        lambda row: next(
            (
                year
                for year in range(
                    DESIRED_ACTUAL_GDP_DATA_YEAR - 1, FIRST_GDP_DATA_YEAR - 1, -1
                )
                if not math.isnan(row[str(year)])
            ),
            np.nan,
        ),
        axis=1,
    )

    # Create a column for the last GDP value based on the last year
    usd_gdp_per_capita_df["last_gdp"] = usd_gdp_per_capita_df.apply(
        lambda row: row[str(int(row["last_year"]))]
        if pd.notnull(row["last_year"])
        else np.nan,
        axis=1,
    )

    # Drop unnecessary columns
    usd_gdp_per_capita_df.drop(
        columns=["code_x", "code_y", "name"], errors="ignore", inplace=True
    )
    usd_gdp_per_capita_df.drop(
        columns=list(map(str, range(FIRST_GDP_DATA_YEAR, LAST_GDP_DATA_YEAR + 1))),
        errors="ignore",
        inplace=True,
    )

    # Add global rank (which for now is = agency_score):
    usd_gdp_per_capita_df["gdp_bucket"] = round(usd_gdp_per_capita_df["last_gdp"].rank(
        pct=True
    ) * 10)
    usd_gdp_per_capita_df["agency_score"] = usd_gdp_per_capita_df["gdp_bucket"]

    return usd_gdp_per_capita_df