"""Recreate the hourly target used in the archived notebooks from UCI data."""

import argparse
import zipfile
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True, help="Downloaded UCI ZIP archive")
    parser.add_argument(
        "--output", type=Path, default=Path("data/clean_hourly_data.csv"),
        help="Output CSV path (default: data/clean_hourly_data.csv)",
    )
    args = parser.parse_args()

    with zipfile.ZipFile(args.archive) as archive:
        with archive.open("household_power_consumption.txt") as source:
            minute_data = pd.read_csv(
                source, sep=";", usecols=["Date", "Time", "Global_active_power"],
                na_values=["?"], low_memory=False,
            )

    minute_data["ds"] = pd.to_datetime(
        minute_data["Date"] + " " + minute_data["Time"],
        format="%d/%m/%Y %H:%M:%S",
    )
    minute_data = minute_data.sort_values("ds")
    minute_data["Global_active_power"] = pd.to_numeric(
        minute_data["Global_active_power"], errors="raise"
    )
    if minute_data["ds"].duplicated().any():
        raise ValueError("Duplicate minute timestamps in source archive")

    # The original notebooks' saved summary statistics match forward filling
    # missing minute readings, summing each hour, and dropping partial hours.
    power = minute_data.set_index("ds")["Global_active_power"].ffill()
    hourly = power.resample("h").sum().iloc[1:-1].round(2)
    result = hourly.rename("y").reset_index()

    if len(result) != 34_587 or result.iloc[0]["y"] != 217.93 or result.iloc[-1]["y"] != 69.82:
        raise ValueError("Reconstructed data does not match the archived notebook outputs")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, date_format="%Y-%m-%d %H:%M:%S", float_format="%.2f")
    print(f"Wrote {len(result):,} hourly rows to {args.output}")


if __name__ == "__main__":
    main()
