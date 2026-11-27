# Alabama Voter Registration and Participation

An exploratory county-level analysis of Alabama voter registration and election participation using locally supplied registration and racial-participation workbooks.

## Project scope

The original analysis combines county registration records with 2020 and 2024 participation data. It examines 2024 inactive-registration rates and a turnout proxy, then compares a small set of counties with manually supplied polling-place counts.

This repository contains code and documentation only. Source workbooks are not included because they were stored locally and may have access or redistribution restrictions.

## Data inputs

Provide two Excel workbooks when running the script:

1. A registration workbook with `year`, `county`, `inactive_total`, `total_active_inactive`, and `active_total`.
2. A participation workbook with `Year`, `county`, and `total_ballots_cast`.

The script standardizes `Year` to `year` and joins records on county and year. Verify that the workbooks use consistent county names and comparable definitions before interpreting results.

## Run

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python alabama_voter_analysis.py --registration path/to/registration.xlsx --participation path/to/participation.xlsx --output-dir outputs
```

The script writes three PNG charts to the output folder: inactive-registration rate by county, the turnout proxy by county, and polling-place availability versus the turnout proxy for seven counties with supplied polling-place counts.

## Definitions and limitations

- **Inactive-registration rate** is calculated as inactive registrations divided by the workbook's `total_active_inactive` field. Confirm that this denominator matches the source's official definition.
- **Turnout proxy** is ballots cast divided by active registrations. It is a county-level ratio, not an individual turnout rate; it can exceed 1 if the files use different universes or reporting periods.
- Polling-place counts are manually entered for seven counties only. This small, incomplete comparison cannot establish an effect of polling access on turnout.
- The original code included race-specific rates, but the field definitions and denominators need verification before they can be presented as race-specific turnout. They are omitted from the cleaned workflow until those definitions are confirmed.
- These are descriptive aggregates. They do not establish causal relationships or account for uncertainty, demographic composition, election type, or reporting differences.
- Check the source workbook documentation and applicable terms before publishing data or derived tables.

## Files

| File | Purpose |
| --- | --- |
| `alabama_voter_analysis.py` | Loads the two workbooks, validates required fields, computes documented ratios, and creates charts. |
| `requirements.txt` | Python dependencies. |
| `.gitignore` | Excludes local workbooks and generated outputs. |
