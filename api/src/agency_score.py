# 👉 Agency Score

import os
import pandas as pd
import numpy as np
import math
from country_data import get_reference_countries_df, get_reference_countries_df, normalize_name, get_all_countries_in_the_world_df

# from country_data import get_usd_gdp_per_capita_df

# 👉  Explanation: How do we quantify a country's agency and means to implement changes?
#
# To start with, we will just use GDP data (the crudest representation of agency)
#
# While that's important in a money-driven world, there's other facilitators of change:
#
#  - Education
#  - National Governance standards?
#  - Infrastructure (roads, communications...)
#  - In general, where they stand in the battle to overcome their intrinsic challenges!
#
# NOTE: in a way, this is the reverse of our other "Challenges Score" and perhaps they
# could be merged into an "Agency" score that can have positive or negative sign 🤔
#
# OTOH, a country could face great challenges and ALSO have a lot of agency
# to tackle them (say, Australia faces desertification and off-the-charts temps,
# but it's also a wealthy country with above-average agency)
#
# ➡️ Work in progress!

# 👉 GDP data per Country
def get_gdp_data():
    # Fetch CSV file (uploaded to Files tab)
    usd_gdp_per_capita_df = pd.read_csv(os.getcwd() +"/data/hex/Fair Water - NGDPDPC (1).csv")

    # Normalise names:
    usd_gdp_per_capita_df["country"] = usd_gdp_per_capita_df["country"].apply(
        lambda x: normalize_name(x)
    )

    # Merge with all_countries_in_the_world_df to get country ISO code
    usd_gdp_per_capita_df = usd_gdp_per_capita_df.merge(
        get_all_countries_in_the_world_df(), left_on="country", right_on="name", how="left"
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
    usd_gdp_per_capita_df.rename(columns={'country': 'name'}, inplace=True)

    # Add global rank (which for now is = agency_score):
    usd_gdp_per_capita_df["gdp_rank"] = round(usd_gdp_per_capita_df["last_gdp"].rank())
    usd_gdp_per_capita_df["gdp_bucket"] = round(usd_gdp_per_capita_df["last_gdp"].rank(
        pct=True
    ) * 10)
    usd_gdp_per_capita_df["agency_score"] = usd_gdp_per_capita_df["gdp_bucket"]

    return usd_gdp_per_capita_df


# 👉 Explanation: get_agency_score()
#
# And here's the ACTUAL calculation of our "Agency Score" (per GDP global rank).
#
# This is our way to try to quantify how much "muscle" a country faces
# when trying to improve water access for it's citizens.
#
# This follows (or should follow) the standard from the other get_xxx_score() functions.

# magic prompt used: refactor get_agency_score function to return a score of 1-10 based on where the country's per capita GDP falls in the global ranking. So the country with the biigest gdp per capita gets a 10, and the lowest gets a 1 score (and so on for the others according to which 10% bucket they fall in)

def get_agency_score(usd_gdp_per_capita_df, iso_country_code):
    try:
        country = usd_gdp_per_capita_df.loc[iso_country_code]
    except KeyError:
        country = None
    
    # if country code not in GDP list return None
    if country is None:
        print(f"  Warning: '{iso_country_code}' not found in usd_gdp_per_capita_df - returning None")
        return None

    # Find the country's Agency Score
    score = country["agency_score"]
    return score

# # Self-test:
# def test(iso_code):
#     print(f" - Test '{iso_code}' agency score: {get_agency_score(iso_code)}\n")

# print("Self-tests (these don't affect function output):\n")
# print("Single country test ('UY'):\n")
# test("UY")
# print("Countries in 'reference_countries_df':\n")
# for country_code in reference_countries_df.index:
#     test(country_code)
# print("Bad country code ('++' -> 'None'):")
# test("++")