import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib
from shutil import move

def fetch_latest_ardd():
    """
    Placeholder for future data scraping.
    Will download the latest Excel file from BITRE once the site stabilizes.
    """
    print("⚠️ fetch_latest_ardd is not yet implemented due to unstable download endpoint.")
    pass

def find_latest_bitre_file(folder="data"):
    """
    Scans the provided folder for the latest bitre_fatal_crashes_*.xlsx file.
    Returns the Path object of the most recently modified file.
    """
    files = list(Path(folder).glob("bitre_fatal_crashes_*.xlsx"))
    if not files:
        raise FileNotFoundError("❌ No BITRE Excel file found in data folder.")
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    print(f"📂 Using latest Excel file: {latest_file.name}")
    return latest_file

def hash_file(path):
    """Return SHA256 hash of file contents."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def log_processing(filename, crash_rows, count_rows, status, file_hash):
    """
    Append processing metadata to a log file.
    """
    log_path = Path("data/processing_log.txt")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_line = f"{timestamp} | Processed: {filename} | Crash Rows: {crash_rows:,} | Count Rows: {count_rows:,} | {status} | Hash: {file_hash}\n"

    with open(log_path, "a") as f:
        f.write(log_line)

def extract_crash_data(
    excel_path=None,
    crash_output_csv="data/Crash_Data.csv",
    count_output_csv="data/Crash_Count_By_Date.csv",
    force=False,
    archive=True
):
    """
    Extracts and cleans two sheets from the BITRE Excel workbook:
    - 'BITRE_Fatal_Crash' → Crash data
    - 'BITRE_Fatal_Crash_Count_By_Date' → Aggregated time series

    Saves cleaned versions as CSV files. Returns the two DataFrames.
    """
    if excel_path is None:
        excel_file = find_latest_bitre_file("data")
    else:
        excel_file = Path(excel_path)

    crash_output_file = Path(crash_output_csv)
    count_output_file = Path(count_output_csv)

    # Ensure output directory exists
    crash_output_file.parent.mkdir(parents=True, exist_ok=True)
    count_output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f"🔄 Loading Excel workbook: {excel_file}")

        # Check for duplicate based on hash
        file_hash = hash_file(excel_file)
        log_file = Path("data/processing_log.txt")
        if log_file.exists():
            with open(log_file) as f:
                if file_hash in f.read():
                    if not force:
                        print("⚠️ File has already been processed. Skipping (use force=True to override).")
                        return None, None

        # Load Crash Data (skip first 4 rows of headers)
        crash_df = pd.read_excel(excel_file, sheet_name="BITRE_Fatal_Crash", skiprows=4)

        # Load Time Series Data (skip first 2 rows of headers)
        count_df = pd.read_excel(excel_file, sheet_name="BITRE_Fatal_Crash_Count_By_Date", skiprows=2)

        # Drop fully empty columns
        print("🧹 Cleaning data...")
        crash_df.dropna(axis=1, how='all', inplace=True)
        count_df.dropna(axis=1, how='all', inplace=True)

        # Save cleaned CSVs
        print("💾 Saving cleaned data...")
        crash_df.to_csv(crash_output_file, index=False)
        count_df.to_csv(count_output_file, index=False)

        print(f"✅ Crash data saved to: {crash_output_file}")
        print(f"✅ Aggregated crash count saved to: {count_output_file}")

        log_processing(
            filename=excel_file.name,
            crash_rows=len(crash_df),
            count_rows=len(count_df),
            status="✅ Success",
            file_hash=file_hash
        )

        # Archive the processed Excel file if requested
        if archive:
            archive_dir = Path("data/archive")
            archive_dir.mkdir(parents=True, exist_ok=True)
            # Add timestamp to archived filename to prevent overwrites
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_file_name = f"{excel_file.stem}_{timestamp_str}{excel_file.suffix}"
            archived_file = archive_dir / archived_file_name
            # Check if somehow the generated name already exists (highly unlikely with timestamp)
            if archived_file.exists():
                 print(f"⚠️ Archive file {archived_file} already exists. Skipping move.")
            else:
                move(str(excel_file), str(archived_file))
                print(f"📦 Archived Excel file to: {archived_file}")

        return crash_df, count_df

    except FileNotFoundError:
        print(f"❌ Error: Excel file not found at {excel_file}")
        return None, None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None, None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract and clean BITRE crash data.")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if already processed")
    parser.add_argument("--no-archive", action="store_true", help="Do not move the Excel file to /data/archive")

    args = parser.parse_args()

    extract_crash_data(force=args.force, archive=not args.no_archive)
