# 👉 (FairWater) Country Name Standard
#
# Problem: Different data sources have different spellings of country names, and somethimes we need to join country data from different sources by country name!
#
# Approach: we will set and enforce our own standard:
#
#   1) "known_country_names" holds our preferred names, & maps them
#      to the different spellings we come across in our data
#      (an evolving standard)
#
#   2) The function "normalize_name(country_name)" uses this map, and translates
#      a non-standard name into our standard, or "normalizes" it
#      (this function is used throughout the project)

from known_country_names import known_country_names
from all_countries_in_the_world import all_countries_in_the_world
import pandas as pd
import json

# Use this function to normalise your data and get the ISO 2-letter code from all_countries_in_the_world_df

def normalize_name(country_name):
    for preferred_name, aliases in known_country_names.items():
        if country_name == preferred_name or country_name in aliases:
            return preferred_name
    return country_name

    # def self_test(name):
    #     print(name, "is normalized to", normalize_name(name))

    # print("Self test (does not affect function result):\n\n")
    # self_test("República Oriental del Uruguay")
    # self_test("Ivory Coast")
    # self_test("Côte d ́Ivoire")
    # self_test("Congo, The Democratic Republic of the")
    # self_test("Afghanistan")

# 👉 Next we setup a "base" list containing All Countries in the World.
#
# NOTE this includes *all* countries, not just UN Resolution signatory countries.
#
# This list doesn't change often so we kept it as a simple JSON list with name,
# and ISO Code (a.k.a. ISO "alpha_2" country code) copied and pasted from:
#
#    https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
#
# We then turn this into a DF ("all_countries_in_the_world_df") and "normalize"
# the country names in it using normalize_name() function.
#
# "all_countries_in_the_world_df" is used for the country-selection drop-down list in the App, and from there
# we look up information in other DFs using (usually) the 2-letter ISO country code.


# 👉 Explanation: where to get missing country data?
#
# Look at normalize_country_name Function above!
#   - Add weird country names there as they show up in data!
#   - Use that function to normalise your data and get the ISO 2-letter code from all_countries_in_the_world_df

# Other:
#
# ISO data from https://www.iso.org/obp/ui/#home
# Flags from https://emojipedia.org/
# All countries in the world JSON data: https://gist.github.com/keeguon/2310008

def get_countries_data_as_list():
    with open('data/countries.json') as f:
        jd = json.load(f)
    return list(jd.values())

# 👉 All Countries in the World (DF with normalized country names)
#
def get_all_countries_in_the_world_df():
    # all_countries_in_the_world_df = pd.DataFrame(all_countries_in_the_world)
    all_countries_in_the_world_df = pd.DataFrame(get_countries_data_as_list())
    # pepe.style

    # Normalize names:
    all_countries_in_the_world_df["name"] = all_countries_in_the_world_df["name"].apply(
        lambda x: normalize_name(x)
    )

    return all_countries_in_the_world_df

# 👉 Reference countries:
#
# In addition to showing a list of scores across all countries
# and showing scores for a specific country, we define here a
# list of countries that can represent different stages of development,
# agency, or challenges (sort of like "personnas" but for countries).
#
# The idea is to be able to use these as benchmarks we can compare our
# selected country against and put the numbers in perspective.

# Create the pandas DataFrame from a list of lists
def get_reference_countries_df():
    reference_countries_df = pd.DataFrame(
        [['NO', "Norway"], ["FR", "France"], ["EG", "Egypt"], ['KE', "Kenya"], ['ZA', "South Africa"]],
        columns=['code', 'name']
    )

    # Normalize names, just in case known_country_names changes later
    reference_countries_df["name"] = reference_countries_df["name"].apply(
        lambda x: normalize_name(x)
    )

    # Index by ISO (alpha_2) code:
    reference_countries_df.set_index("code", inplace = True)

    return reference_countries_df


