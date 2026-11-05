# PantryPal
A household ingredient management system and recipe recommendation

## Fresh recipe demo dataset — v3 (2026-10-15)

A clean rebuild is in `data/demo_analysis_v3/`, generated from the unchanged `IndianFoodDatasetCSV.csv.zip` source. The legacy `data/Analysis` and `data/Analysis2` folders have been moved to `data/archive_legacy_analysis/` for recovery; the old `data/processed/` folder remains untouched until the new exports are integrated.

Validated snapshot: 1,000 unique recipes, 623 canonical ingredients, 791 aliases, 12,218 recipe–ingredient links, and 30 demo recipes. Quality checks passed; see `data/demo_analysis_v3/audit/quality_report.json` and `data/demo_analysis_v3/audit/validation_checks.json`.

To rebuild and verify the new dataset, run `python data\\demo_analysis_v3\\run_all.py` from the project root.
