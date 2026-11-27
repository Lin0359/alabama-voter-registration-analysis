# Alabama Voter Registration and Participation

An exploratory county-level analysis of Alabama voter registration and election participation. The current workflow filters both supplied workbooks to 2024 and produces descriptive metrics and charts.

## Scope

This is a cross-sectional, county-level project. It does not estimate individual voting behavior or establish that polling access causes turnout. Source workbooks are not included; obtain the original files and verify their provenance, definitions, and reuse terms before drawing conclusions or sharing derived data.

## Data inputs

Run the script with two Excel workbooks:

- Registration workbook columns: `year`, `county`, `inactive_total`, `total_active_inactive`, and `active_total`.
- Participation workbook columns: `year`, `county`, and `total_ballots_cast`.

Column names are matched without regard to case. County names are trimmed and converted to uppercase before joining. Numeric values may contain commas. The code sums duplicate county rows, so confirm that repeated rows are additive records rather than duplicate snapshots. Only counties present in both files are retained.

## Run

Requires Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
python analyze_alabama_voters.py --registration path/to/registration.xlsx --participation path/to/participation.xlsx --output-dir outputs
```

The script writes two CSV files and three PNG charts to `outputs/`: county metrics, a seven-county polling-count subset, inactive-registration rate by county, turnout proxy by county, and the transcribed polling-location counts.

## Measures and limitations

- **Inactive-registration rate:** `inactive_total / total_active_inactive`. Check that the denominator matches the source workbook's definition.
- **Turnout proxy:** `total_ballots_cast / active_total`. This is an aggregate ratio, not an individual turnout rate; it may exceed 1 when source populations or reporting periods differ.
- **Polling locations:** counts are manually transcribed for Autauga (12), Baldwin (39), Bibb (8), Blount (18), Bullock (6), Butler (10), and Calhoun (25). The original source for these counts must be checked before reuse. Seven counties are not a representative statewide sample, and the chart does not support a causal claim.
- The present workflow does not calculate race-specific metrics or compare years. Those analyses require documented field meanings, denominators, and comparable source coverage.
- Results are descriptive and sensitive to differences in source definitions, election type, and reporting.

## Repository files

| File | Purpose |
| --- | --- |
| `analyze_alabama_voters.py` | Reproducible data preparation, metrics, and chart generation. |
| `requirements.txt` | Python dependencies. |
| `.gitignore` | Excludes local spreadsheets, generated outputs, and Python cache/virtual-environment files. |

## Next improvement

Add source links, retrieval dates, and a data dictionary once the exact workbook versions used in the original report are available.
