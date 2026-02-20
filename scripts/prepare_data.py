"""prepare_data.py — Transform a manually downloaded BITRE fatalities Excel
file into a clean CSV ready for analysis.

Usage:
    python scripts/prepare_data.py data/bitre_fatalities_dec2025.xlsx

The script validates the file's structure against what the notebooks expect
and prints clear warnings before writing data/Crash_Data.csv.
"""

import sys
from pathlib import Path

import pandas as pd

# Allow importing data_cleaning from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))
from data_cleaning import full_clean_pipeline


# ---------------------------------------------------------------------------
# What we expect the file to look like
# ---------------------------------------------------------------------------
# This is the column set from the Dec 2025 release. If BITRE renames or drops
# something, the script will tell you exactly what changed rather than failing
# silently mid-analysis.
EXPECTED_COLUMNS = {
    'Crash ID', 'State', 'Month', 'Year', 'Dayweek', 'Time',
    'Crash Type', 'Bus Involvement', 'Heavy Rigid Truck Involvement',
    'Articulated Truck Involvement', 'Speed Limit', 'Road User',
    'Gender', 'Age', 'National Remoteness Areas 2021', 'SA4 Name 2021',
    'National LGA Name 2021', 'National Road Type', 'Christmas Period',
    'Easter Period',
}

# The specific category values each notebook depends on. If BITRE adds a new
# road user type or renames one, the warning will catch it before it causes a
# silent gap in a chart.
EXPECTED_CATEGORICALS = {
    'Road User': {
        'Driver', 'Passenger', 'Pedestrian', 'Pedal cyclist',
        'Motorcycle rider', 'Motorcycle pillion passenger', 'Unknown',
    },
    'Gender': {'Male', 'Female', 'Unknown'},
    'Crash Type': {'Single', 'Multiple', 'Unknown'},
}

# Sheet names BITRE has used across releases, in order of preference.
KNOWN_SHEET_NAMES = ['BITRE_Fatality', 'BITRE_Fatal_Crash']


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def find_fatality_sheet(xl_path):
    """Return the name of the crash-level sheet, trying known names in order.

    pd.ExcelFile lets us inspect sheet names without loading the whole file.
    If neither expected name is found we fall back to the first sheet and warn,
    so the script degrades gracefully rather than crashing.
    """
    xl = pd.ExcelFile(xl_path)
    for name in KNOWN_SHEET_NAMES:
        if name in xl.sheet_names:
            return name

    print(f"  WARNING: Could not find a recognised sheet name.")
    print(f"           Available sheets: {xl.sheet_names}")
    print(f"           Falling back to first sheet: '{xl.sheet_names[0]}'")
    return xl.sheet_names[0]


def find_header_row(xl_path, sheet_name, anchor='Crash ID', max_rows=10):
    """Scan the first rows of a sheet to find the one containing `anchor`.

    BITRE puts a preamble (title, date, notes) above the actual table.
    Instead of hardcoding skiprows=4, we search for the column header we know
    must exist. This survives BITRE adding or removing a preamble line.

    We load with header=None so pandas treats everything as plain data, then
    iterate over rows looking for a cell that matches our anchor string.
    """
    raw = pd.read_excel(xl_path, sheet_name=sheet_name, header=None, nrows=max_rows)

    for i, row in raw.iterrows():
        if anchor in row.values:
            return i  # 0-based row index — pass directly to pd.read_excel(header=i)

    raise ValueError(
        f"Could not find '{anchor}' in the first {max_rows} rows of "
        f"sheet '{sheet_name}'. Has the file format changed significantly?"
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_columns(df_columns, expected):
    """Warn about columns that are missing or newly added.

    'Missing' means the notebook code references them and will break.
    'Extra' is informational — new columns you might want to use.
    """
    found   = set(df_columns)
    missing = expected - found
    extra   = found - expected

    if missing:
        print(f"  WARNING: Expected columns not found — {sorted(missing)}")
        print( "           Code referencing these columns will break.")
    if extra:
        print(f"  NOTE: New columns in this release — {sorted(extra)}")
        print( "        Add them to EXPECTED_COLUMNS if you want to track them.")
    if not missing and not extra:
        print("  Columns: OK")


def validate_categoricals(df, expected_cats):
    """Warn about category values that are new or have disappeared.

    We do this before cleaning so we're comparing the raw source values,
    not the ones we've already mapped to NaN.
    """
    all_ok = True
    for col, expected_vals in expected_cats.items():
        if col not in df.columns:
            continue
        found_vals = set(df[col].dropna().unique())
        new_vals   = found_vals - expected_vals
        gone_vals  = expected_vals - found_vals

        if new_vals:
            print(f"  WARNING: '{col}' has new values — {sorted(new_vals)}")
            print( "           Check whether these need handling in data_cleaning.py.")
            all_ok = False
        if gone_vals:
            print(f"  NOTE: '{col}' no longer contains — {sorted(gone_vals)}")
            all_ok = False

    if all_ok:
        print("  Categoricals: OK")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def prepare(xl_path, output_csv='data/Crash_Data.csv'):
    xl_path = Path(xl_path)

    if not xl_path.exists():
        print(f"ERROR: File not found: {xl_path}")
        sys.exit(1)

    print(f"\nLoading: {xl_path.name}")

    # 1. Find the right sheet
    sheet = find_fatality_sheet(xl_path)
    print(f"  Sheet: '{sheet}'")

    # 2. Find header row without assuming a fixed number of preamble lines
    header_row = find_header_row(xl_path, sheet)
    print(f"  Header at row {header_row + 1}")  # +1 for human-readable 1-indexed display

    # 3. Load with the correct header row; drop any fully-empty trailing columns
    df = pd.read_excel(xl_path, sheet_name=sheet, header=header_row)
    df.dropna(axis=1, how='all', inplace=True)
    print(f"  {len(df):,} rows × {len(df.columns)} columns")
    print(f"  Year range in source: {int(df['Year'].min())}–{int(df['Year'].max())}")

    # 4. Validate structure before touching the data
    print("\nValidating structure...")
    validate_columns(df.columns, EXPECTED_COLUMNS)
    validate_categoricals(df, EXPECTED_CATEGORICALS)

    # 5. Clean and derive columns
    print("\nCleaning...")
    df = full_clean_pipeline(df)
    print(f"  {len(df):,} rows after dropping current incomplete year")

    # 6. Save
    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved → {out}  ({len(df):,} rows, {len(df.columns)} columns)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    prepare(sys.argv[1])
