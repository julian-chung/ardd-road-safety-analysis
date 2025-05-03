import pandas as pd
import numpy as np
import warnings
import datetime

def load_ardd_data(filepath):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.DtypeWarning)
        df = pd.read_csv(filepath, low_memory=False)
    return df
    
def replace_missing_values(df):
    """Replace known placeholders with NaN and standardise gender."""
    df.replace('-9', np.nan, inplace=True)
    df.replace('Unspecified', np.nan, inplace=True)
    df.replace('Other/-9', np.nan, inplace=True)

    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].str.strip()
        df['Gender'] = df['Gender'].replace({
            '-9': np.nan,
            'M ': 'Male',
            'F ': 'Female'})
    return df

def drop_partial_year(df):
    """Remove data from the current calendar year as it may be incomplete."""
    if 'Year' in df.columns:
        current_year = datetime.date.today().year
        df = df[df['Year'] != current_year].copy() # Uses current_year and ensure a copy is returned
    return df

def drop_unused_columns(df):
    """
    Drop columns with high proportion of missing data or administrative labels
    that change naming convention across years (e.g. SA4, LGA, Remoteness Areas).
    """
    substrings_to_drop = [
        "Heavy Rigid Truck Involvement",
        "National Remoteness Areas",
        "SA4 Name",
        "National LGA Name",
        "National Road Type"
    ]

    cols_to_drop = [
        col for col in df.columns
        if any(sub in col for sub in substrings_to_drop)
    ]

    df.drop(columns=cols_to_drop, inplace=True)
    return df


def map_month_names(df):
    """Map numeric months to month names for better readability."""
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
        6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
        11: 'November', 12: 'December'
    }
    if 'Month' in df.columns:
        df['Month Name'] = df['Month'].map(month_names)
    return df

def full_clean_pipeline(filepath="../data/Crash_Data.csv"):
    """Run the complete cleaning process."""
    df = load_ardd_data(filepath)
    df = replace_missing_values(df)
    df = map_month_names(df)
    df = drop_partial_year(df) 
    df = drop_unused_columns(df)
    return df
