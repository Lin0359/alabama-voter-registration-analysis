"""Explore Alabama county-level voter registration and participation data.

Input files are supplied by the user; this script does not download or redistribute them.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

POLLING_PLACES = {
    "AUTAUGA": 12, "BALDWIN": 39, "BIBB": 8, "BLOUNT": 18,
    "BULLOCK": 6, "BUTLER": 10, "CALHOUN": 25,
}


def load_table(path: Path, required: set[str], label: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    if "year" not in df.columns and "election_year" in df.columns:
        df = df.rename(columns={"election_year": "year"})
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} is missing columns: {sorted(missing)}")
    df["county"] = df["county"].astype(str).str.strip().str.upper()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", required=True, type=Path, help="Registration workbook")
    parser.add_argument("--participation", required=True, type=Path, help="Ballots-cast workbook")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    registration = load_table(
        args.registration,
        {"year", "county", "inactive_total", "total_active_inactive", "active_total"},
        "Registration workbook",
    )
    participation = load_table(
        args.participation, {"year", "county", "total_ballots_cast"}, "Participation workbook"
    )
    for col in ["inactive_total", "total_active_inactive", "active_total"]:
        registration[col] = pd.to_numeric(registration[col], errors="coerce")
    participation["total_ballots_cast"] = pd.to_numeric(
        participation["total_ballots_cast"], errors="coerce"
    )

    reg24 = registration.loc[registration["year"] == 2024].copy()
    reg24["inactive_rate"] = reg24["inactive_total"].div(
        reg24["total_active_inactive"].where(reg24["total_active_inactive"] != 0)
    )
    turnout24 = participation.loc[participation["year"] == 2024].copy()
    merged = reg24.merge(turnout24, on=["year", "county"], how="inner", validate="one_to_one")
    merged["turnout_proxy"] = merged["total_ballots_cast"].div(
        merged["active_total"].where(merged["active_total"] != 0)
    )
    merged = merged.sort_values("turnout_proxy", ascending=False)
    merged.to_csv(args.output_dir / "county_metrics_2024.csv", index=False)

    for metric, title, filename in [
        ("inactive_rate", "Inactive share of active and inactive registrations (2024)", "inactive_rate_2024.png"),
        ("turnout_proxy", "Ballots cast / active registrations (2024 turnout proxy)", "turnout_proxy_2024.png"),
    ]:
        plot_data = merged.dropna(subset=[metric]).sort_values(metric)
        fig, ax = plt.subplots(figsize=(10, max(5, len(plot_data) * 0.22)))
        ax.barh(plot_data["county"], plot_data[metric], color="#3274A1")
        ax.set(title=title, xlabel="Ratio", ylabel="County")
        fig.tight_layout()
        fig.savefig(args.output_dir / filename, dpi=180)
        plt.close(fig)

    polling = merged.loc[merged["county"].isin(POLLING_PLACES)].copy()
    polling["polling_places"] = polling["county"].map(POLLING_PLACES)
    polling["registered_voters_per_polling_place"] = polling["active_total"].div(
        polling["polling_places"].where(polling["polling_places"] != 0)
    )
    polling.to_csv(args.output_dir / "polling_access_subset_2024.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    p = polling.sort_values("registered_voters_per_polling_place")
    ax.barh(p["county"], p["registered_voters_per_polling_place"], color="#E1812C")
    ax.set(title="Active registrations per polling place in selected counties (2024)",
           xlabel="Registrations per reported polling place", ylabel="County")
    fig.tight_layout()
    fig.savefig(args.output_dir / "polling_access_subset_2024.png", dpi=180)
    plt.close(fig)
    print(f"Wrote analysis outputs to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
