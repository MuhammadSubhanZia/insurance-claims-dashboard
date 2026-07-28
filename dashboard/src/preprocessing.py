import pandas as pd
import numpy as np
import unicodedata
from src.config import DATA_PATH, LOCATION_MAPPING_PATH
from src.mappings import (
    reason_mapping,
    placeholder_numbers,
    debtor_type_mapping,
    status_mapping
)

# Text cleaner
def clean_text(text):

    if pd.isna(text):
        return np.nan

    text = unicodedata.normalize("NFKC", str(text))

    text = " ".join(text.split())

    return text.strip()


# Location Standardizer
def standardize_locations(df):

    mapping = pd.read_excel(
        LOCATION_MAPPING_PATH
    )

    mapping_dict = dict(
        zip(
            mapping["Original"],
            mapping["Standardized"]
        )
    )

    df["Location"] = (
        df["Accident Location"]
        .apply(clean_text)
        .map(mapping_dict)
    )

    # Missing/unmapped accident locations are kept as an explicit
    # "Unknown" category instead of silently dropping out of group-bys.
    df["Location"] = df["Location"].fillna("Unknown")

    return df


# Recovery Reason Standardizer
def standardize_reasons(df):

    df["Recovery Reason"] = (
        df["Recovery Reason"]
        .apply(clean_text)
        .replace(reason_mapping)
    )

    df["Recovery Reason"] = (
        df["Recovery Reason"]
        .fillna("Not Specified")
    )

    return df


# Debtor Type Standardizer
def standardize_debtor_type(df):

    df["Debtor Type"] = (
        df["Debtor Type"]
        .apply(clean_text)
        .map(debtor_type_mapping)
        .fillna("Unknown")
    )

    return df


# Status Standardizer
def standardize_status(df):
    """
    The raw Status column mixes an English label with an Arabic
    description in the same cell. This keeps the clean English label
    for filtering/KPIs and preserves the full raw text for reference.
    """

    df["Status Detail"] = df["Status"]

    df["Status"] = (
        df["Status"]
        .apply(clean_text)
        .map(status_mapping)
    )

    df["Status"] = df["Status"].fillna("Unknown")

    return df


# Officer cleaner
def standardize_officer(df):

    df["Officer"] = (
        df["Officer"]
        .apply(clean_text)
        .fillna("Unassigned")
    )

    return df


# Debtor Flag
def flag_placeholder_numbers(df):

    df["Debtor Number Status"] = np.where(

        df["Debtor Number"].isin(
            placeholder_numbers
        ),

        "Placeholder",

        "Valid"

    )

    return df


# Date Conversion
def convert_dates(df):

    df["Accident Date"] = pd.to_datetime(
        df["Accident Date"],
        errors="coerce"
    )

    df["RCP Date"] = pd.to_datetime(
        df["RCP Date"],
        format="%y-%m-%d",
        errors="coerce"
    )

    return df


def prepare_data(data=DATA_PATH):

    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.read_excel(data)

    df = convert_dates(df)
    df = standardize_locations(df)
    df = standardize_reasons(df)
    df = standardize_debtor_type(df)
    df = standardize_status(df)
    df = standardize_officer(df)
    df = flag_placeholder_numbers(df)

    # Derived Feature
    df["Recovery Delay (Days)"] = (
        df["RCP Date"] - df["Accident Date"]
    ).dt.days

    return df
