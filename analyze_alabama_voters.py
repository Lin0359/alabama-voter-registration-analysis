#!/usr/bin/env python3
"""Build a 2024 county-level Alabama voter registration analysis."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

YEAR = 2024
POLLING_LOCATIONS = {
    "AUTAUGA": 12,
    "BALDWIN": 39,
    "BIBB": 8,
    "BLOUNT": 18,
    "BULLOCK": 6,
    "BUTLER": 10,
    "CALHOUN": 25,
}


def load_workbook(path: Path, required: set[str], label: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} workbook is missing columns: {', '.join(sorted(missing))}")
    df["county"] = df["county"].astype("string").str.strip().str.upper()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df.loc[df["year"].eq(YEAR)].copy()


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.replace(",", "", regex=False), errors="coerce")


def save_bar(data: pd.DataFrame, x: str, y: str, title: str, ylabel: str, path: Path) -> None:
    plot_data = data.dropna(subset=[x, y]).sort_values(y, ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(plot_data[x], plot_data[y], color="#2673a6")
    ax.set(title=title, xlabel="County", ylabel=ylabel)
    ax.tick_params(axis="x", rotation=70)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", type=Path, required=True, help="Registration Excel workbook")
    parser.add_argument("--participation", type=Path, required=True, help="Election participation Excel workbook")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    registration = load_workbook(
        args.registration,
        {"year", "county", "inactive_total", "total_active_inactive", "active_total"},
        "Registration",
    )
    participation = load_workbook(
        args.participation, {"year", "county", "total_ballots_cast"}, "Participation"
    )
    if registration.empty or participation.empty:
        raise ValueError(f"No {YEAR} rows found in one or both workbooks.")

    for col in ("inactive_total", "total_active_inactive", "active_total"):
        registration[col] = numeric(registration[col])
    participation["total_ballots_cast"] = numeric(participation["total_ballots_cast"])

    # Collapse duplicate county rows before joining; sums preserve county totals.
    reg = registration.groupby("county", as_index=False)[
        ["inactive_total", "total_active_inactive", "active_total"]
    ].sum(min_count=1)
    votes = participation.groupby("county", as_index=False)["total_ballots_cast"].sum(min_count=1)
    metrics = reg.merge(votes, on="county", how="inner", validate="one_to_one")
    metrics["inactive_rate"] = metrics["inactive_total"].div(
        metrics["total_active_inactive"].where(metrics["total_active_inactive"].ne(0))
    )
    metrics["turnout_proxy"] = metrics["total_ballots_cast"].div(
        metrics["active_total"].where(metrics["active_total"].ne(0))
    )
    metrics.to_csv(args.output_dir / "county_metrics_2024.csv", index=False)

    polling = metrics.loc[metrics["county"].isin(POLLING_LOCATIONS)].copy()
    polling["polling_locations_transcribed"] = polling["county"].map(POLLING_LOCATIONS)
    polling.to_csv(args.output_dir / "polling_access_subset_2024.csv", index=False)

    save_bar(metrics, "county", "inactive_rate", "Alabama county inactive registration rate, 2024",
             "Inactive registrations / active + inactive registrations", args.output_dir / "inactive_rate_2024.png")
    save_bar(metrics, "county", "turnout_proxy", "Alabama county turnout proxy, 2024",
             "Ballots cast / active registrations (proxy)", args.output_dir / "turnout_proxy_2024.png")
    save_bar(polling, "county", "polling_locations_transcribed",
             "Polling locations in seven-county subset, 2024 (transcribed counts)",
             "Polling locations (verify source)", args.output_dir / "polling_access_subset_2024.png")
    print(f"Wrote 3 charts and 2 CSV files to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
