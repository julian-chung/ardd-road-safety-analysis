import pandas as pd
import numpy as np
import datetime


def replace_missing_values(df):
    """Replace known placeholders with NaN and standardise categoricals.

    BITRE has used a few different conventions for unknown values across
    releases, so we handle all of them here:
      - Integer -9 and string '-9' for unknown numerics (e.g. Speed Limit, Age)
      - 'Other/-9' (old Road User label) and 'Unknown' (new label)
      - 'Unspecified' (old Gender label) — new label is also 'Unknown'
    Mapping all of these to NaN keeps the rest of the analysis consistent.
    """
    df.replace(-9, np.nan, inplace=True)          # integer sentinel (new format)
    df.replace('-9', np.nan, inplace=True)         # string sentinel (old format)
    df.replace('Other/-9', np.nan, inplace=True)   # old Road User unknown label
    df.replace('Unspecified', np.nan, inplace=True) # old Gender unknown label
    df.replace('Unknown', np.nan, inplace=True)    # new unknown label (all columns)

    if 'Gender' in df.columns:
        # Strip whitespace and fix any old abbreviated codes
        df['Gender'] = df['Gender'].str.strip().replace({'M ': 'Male', 'F ': 'Female'})

    return df


def add_age_group(df):
    """Bin Age into the groups BITRE used to provide as 'Age Group'.

    BITRE dropped this derived column in their newer releases, so we
    re-create it from the raw Age column using pd.cut().

    pd.cut() divides a numeric series into labelled intervals. The bin
    edges are exclusive on the left and inclusive on the right by default,
    so (-1, 16] catches 0–16, (16, 25] catches 17–25, and so on.
    """
    if 'Age' not in df.columns:
        return df

    age = pd.to_numeric(df['Age'], errors='coerce')

    bins   = [-1,       16,       25,       39,       64,       74,          float('inf')]
    labels = ['0_to_16', '17_to_25', '26_to_39', '40_to_64', '65_to_74', '75_or_older']

    df['Age Group'] = pd.cut(age, bins=bins, labels=labels)
    return df


def _parse_hour(df):
    """Parse the Time column to an integer hour (0–23).

    The Time column comes as a string 'HH:MM:SS' in the new XLSX format
    and 'H:MM' in the old CSV. We try both formats and return a Series
    of integer hours (NaN where time couldn't be parsed).
    """
    hour = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.hour
    if hour.isna().all():
        hour = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.hour
    return hour


def add_time_of_day(df):
    """Classify each crash as 'Day' (06:00–17:59) or 'Night' (18:00–05:59).

    np.where(condition, value_if_true, value_if_false) is a fast vectorised
    if/else — much quicker than applying a function row by row.
    We use .between(6, 17) which is inclusive on both ends.
    """
    if 'Time' not in df.columns:
        return df

    hour = _parse_hour(df)

    df['Time of day'] = np.where(hour.between(6, 17), 'Day', 'Night')
    df.loc[hour.isna(), 'Time of day'] = np.nan
    return df


def add_day_of_week(df):
    """Classify each crash as 'Weekday' or 'Weekend'.

    BITRE defined the weekend as the social weekend period rather than
    calendar Saturday/Sunday. Based on the original data, the definition is:

        Weekend = Friday from 18:00 through Monday 05:59 (inclusive)

    We build a boolean mask using three OR conditions and convert to labels
    with np.where.
    """
    if 'Dayweek' not in df.columns or 'Time' not in df.columns:
        return df

    hour = _parse_hour(df)
    day  = df['Dayweek']

    is_weekend = (
        day.isin(['Saturday', 'Sunday'])          |  # always weekend
        ((day == 'Friday') & (hour >= 18))        |  # Friday night onward
        ((day == 'Monday') & (hour < 6))             # early Monday still weekend
    )

    df['Day of week'] = np.where(is_weekend, 'Weekend', 'Weekday')
    df.loc[hour.isna() | day.isna(), 'Day of week'] = np.nan
    return df


def drop_partial_year(df):
    """Remove the current calendar year as it won't be complete yet."""
    if 'Year' in df.columns:
        current_year = datetime.date.today().year
        df = df[df['Year'] != current_year].copy()
    return df


def drop_unused_columns(df):
    """Drop geographic boundary columns that aren't used in the notebooks.

    These columns have very high rates of missing data and their names change
    between BITRE releases (e.g. 'SA4 Name 2016' became 'SA4 Name 2021').
    Matching by substring rather than exact name means this keeps working
    even if the year suffix changes again next release.
    """
    substrings_to_drop = [
        'Heavy Rigid Truck Involvement',
        'National Remoteness Areas',
        'SA4 Name',
        'National LGA Name',
        'National Road Type',
    ]
    cols_to_drop = [
        col for col in df.columns
        if any(sub in col for sub in substrings_to_drop)
    ]
    df.drop(columns=cols_to_drop, inplace=True)
    return df


def map_month_names(df):
    """Add a 'Month Name' column mapping numeric months to full names."""
    month_names = {
        1: 'January',  2: 'February', 3: 'March',    4: 'April',
        5: 'May',       6: 'June',     7: 'July',     8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December',
    }
    if 'Month' in df.columns:
        df['Month Name'] = df['Month'].map(month_names)
    return df


def full_clean_pipeline(df):
    """Apply all cleaning and derivation steps to a raw DataFrame.

    Accepts a DataFrame (not a file path) so the pipeline is decoupled
    from how the data was loaded — the caller handles file I/O.
    """
    df = replace_missing_values(df)
    df = map_month_names(df)
    df = add_age_group(df)
    df = add_time_of_day(df)
    df = add_day_of_week(df)
    df = drop_partial_year(df)
    df = drop_unused_columns(df)
    return df
