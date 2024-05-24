import numpy as np

# Final Scores Functions

# Accountability Score:
#
# How much did the country actually do (=progress)
# vs. what they promised (=commitment)
#
def get_accountability_score(commitment, challenge, agency, progress):
    score = round(
        progress + challenge - commitment - agency # no weights needed because both are 0-10
    )
    return score


# International Help Priority Score:
#
# Intention: Water access emergencies (without focusing too much on feasibility of projects)
#
# I.e. BfB score might signal Kenya as a top country to target for help. South Sudan might
# need it more, but be bumped down in BfB because projects there are less likely to succeed.
# We still want to know where the emergencies are (i.e. "where are people dying")
#
# With our limited data: what we do is not take commitment into account, and focus on their
# challenges, but tone that down based on their self reliance (= agency + progress)
#
# J: weight against the country's population (bpl)
def get_ihelp_score(commitment, challenge, agency, progress):
    score = round(challenge - agency - progress)
    return score


# Bang for Bucks Score:
#
# Intention: Where are we most likely to have the biggest impact (sooner). We want this to
# take into account not just raw need, but also the likelihood to create sustained impact
# (the chance a project has to succeed and remain)
#
# With our limited data: we focus on how big the need is (=challenge) and whether there is
# already some sort of framework / capabilities in place (=progress).
# Then we bump that up a bit with their commitment, and bump it down a bit with their agency
# (these last to are weighted down to have less impact over challenge and progress)
# 
# J: use p/c gdp as an indicator of how expensive a project there would be
# J: use stability
def get_bfb_score(commitment, challenge, agency, progress):
    score = round(
        challenge + progress + (commitment//2) - (agency//2)
    )
    return score


# Test with some different base-score configurations:
tests = [
    ["Rich rainy country", 5, 2, 10, 6],
    ["Struggling Country", 3, 10, 0, 0],
    ["Struggling but committed country", 7, 10, 0, 0],
    ["'Kenya-like' country", 8, 7, 2, 5],
    ["'South Africa-like' country", 7,6,4,5],
]

print("Self tests:\n")
print("[commitment, challenge, agency, progress]\n")
for params in tests:
    print(
        f"\n\nAccScore{params}=" + str(get_accountability_score(params[1], params[2], params[3], params[4])),
        f"\nIhelpScore{params}=" + str(get_ihelp_score(params[1], params[2], params[3], params[4])),
        f"\nBfbScore{params}=" + str(get_bfb_score(params[1], params[2], params[3], params[4])),
    )


# Final Scores (Accountability, IHelp, and BfB) in a DF:
final_scores_per_country = all_countries_in_the_world_df.copy()

final_scores_per_country["commitment_score"] = final_scores_per_country["code"].apply(
    lambda code: get_commitment_score(code) if pd.notnull(code) else None
)
final_scores_per_country["challenges_score"] = final_scores_per_country["code"].apply(
    lambda code: get_challenges_score(code) if pd.notnull(code) else None
)
final_scores_per_country["agency_score"] = final_scores_per_country["code"].apply(
    lambda code: get_agency_score(code) if pd.notnull(code) else None
)
final_scores_per_country["progress_score"] = final_scores_per_country["code"].apply(
    lambda code: get_progress_score(code) if pd.notnull(code) else None
)

final_scores_per_country = final_scores_per_country.dropna(
    subset=["commitment_score", "challenges_score", "agency_score", "progress_score"]
)

final_scores_per_country["accountability_score"] = final_scores_per_country.apply(
    lambda row: get_accountability_score(
        row["commitment_score"],
        row["challenges_score"],
        row["agency_score"],
        row["progress_score"],
    ),
    axis=1,
)
final_scores_per_country["ihelp_score"] = final_scores_per_country.apply(
    lambda row: get_ihelp_score(
        row["commitment_score"],
        row["challenges_score"],
        row["agency_score"],
        row["progress_score"],
    ),
    axis=1,
)
final_scores_per_country["bfb_score"] = final_scores_per_country.apply(
    lambda row: get_bfb_score(
        row["commitment_score"],
        row["challenges_score"],
        row["agency_score"],
        row["progress_score"],
    ),
    axis=1,
)

final_scores_per_country

# Melted Final Scores:
final_scores_per_country_melted = pd.melt(
    final_scores_per_country,
    id_vars=["code", "name"],
    var_name="score_type",
    value_name="score_value",
)

final_scores_per_country_melted

# Get All (partial) Scores for Selected Country - - - - - - - - - - - - - - - - - - - -

# Check if the country name exists in the dataframe and get the ISO code
if SELECTED_COUNTRY_NAME in all_countries_in_the_world_df["name"].values:
    SELECTED_COUNTRY_ISO_CODE = all_countries_in_the_world_df[
        all_countries_in_the_world_df["name"] == SELECTED_COUNTRY_NAME
    ]["code"].iloc[0]
else:
    SELECTED_COUNTRY_ISO_CODE = None

if SELECTED_COUNTRY_ISO_CODE:
    SELECTED_COUNTRY_COMMITMENT_SCORE = get_commitment_score(SELECTED_COUNTRY_ISO_CODE)
    SELECTED_COUNTRY_CHALLENGES_SCORE = get_challenges_score(SELECTED_COUNTRY_ISO_CODE)
    SELECTED_COUNTRY_AGENCY_SCORE = get_agency_score(SELECTED_COUNTRY_ISO_CODE)
    SELECTED_COUNTRY_PROGRESS_SCORE = get_progress_score(SELECTED_COUNTRY_ISO_CODE)
    SELECTED_COUNTRY_ACCOUNTABILITY_SCORE = get_accountability_score(
        SELECTED_COUNTRY_COMMITMENT_SCORE,
        SELECTED_COUNTRY_CHALLENGES_SCORE,
        SELECTED_COUNTRY_AGENCY_SCORE,
        SELECTED_COUNTRY_PROGRESS_SCORE,
    )
    SELECTED_COUNTRY_IHELP_SCORE = get_ihelp_score(
        SELECTED_COUNTRY_COMMITMENT_SCORE,
        SELECTED_COUNTRY_CHALLENGES_SCORE,
        SELECTED_COUNTRY_AGENCY_SCORE,
        SELECTED_COUNTRY_PROGRESS_SCORE,
    )
    SELECTED_COUNTRY_BFB_SCORE = get_bfb_score(
        SELECTED_COUNTRY_COMMITMENT_SCORE,
        SELECTED_COUNTRY_CHALLENGES_SCORE,
        SELECTED_COUNTRY_AGENCY_SCORE,
        SELECTED_COUNTRY_PROGRESS_SCORE,
    )

    selected_params_df = pd.DataFrame(
        [
            {
                "iso_code": SELECTED_COUNTRY_ISO_CODE or "?",
                "name": SELECTED_COUNTRY_NAME or "none selected",
                "commitment_score": SELECTED_COUNTRY_COMMITMENT_SCORE or np.nan,
                "challenges_score": SELECTED_COUNTRY_CHALLENGES_SCORE or np.nan,
                "agency_score": SELECTED_COUNTRY_AGENCY_SCORE or np.nan,
                "progress_score": SELECTED_COUNTRY_PROGRESS_SCORE or np.nan,
                "accountability_score": SELECTED_COUNTRY_ACCOUNTABILITY_SCORE or np.nan,
                "ihelp_score": SELECTED_COUNTRY_IHELP_SCORE or np.nan,
                "bfb_score": SELECTED_COUNTRY_BFB_SCORE or np.nan,
                # if SELECTED_COUNTRY_PROGRESS_SCORE
                # else np.nan,
            }
        ]
    )

selected_params_df

# Selected Country's Scores as Rows (for App chart) - - - - - - - - - - - - - - - -
selected_params_as_rows_df = selected_params_df.rename(
    columns={
        "commitment_score": "Commitment",
        "challenges_score": "Challenges",
        "agency_score": "Agency",
        "progress_score": "Progress",
        "accountability_score": "Accountability",
        "ihelp_score": "International Help Priority",
        "bfb_score": "Bang For Bucks",
    }
)[
    [
        "Commitment",
        "Challenges",
        "Agency",
        "Progress",
        "Accountability",
        "International Help Priority",
        "Bang For Bucks",
    ]
].melt()

selected_params_as_rows_df


# Find Top Commitment - - - - - - - - - - - - - - - -
top_commitment_country = signatory_countries_df.loc[signatory_countries_df["commitment_score"].idxmax()]
# print(top_commitment_country)
print("\n🏆 The most commited country is", top_commitment_country.flag, top_commitment_country.official_name, f"({top_commitment_country.commitment_score}/10)")
print()

# Find Minimum Commitment Country - - - - - - - - - - - - - - - -
least_commitment_country = signatory_countries_df.loc[signatory_countries_df["commitment_score"].idxmin()]
# print(least_commitment_country)
print("\n😐 The least commited country is", least_commitment_country.flag, least_commitment_country.official_name, f"({top_commitment_country.commitment_score}/10)")

