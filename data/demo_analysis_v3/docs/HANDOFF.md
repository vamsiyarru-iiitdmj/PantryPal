# PantryPal dataset handoff — fresh analysis v3

## Purpose and source

A clean rebuild from the unchanged `IndianFoodDatasetCSV.csv.zip` archive (6,871 source rows). The source has translated names, ingredients, instructions, prep/cook/total time, servings, cuisine, course, diet and URLs. Legacy `data/Analysis` and `data/Analysis2` were moved to `data/archive_legacy_analysis/` for recovery; `data/processed/` remains untouched.

## Final validated snapshot

- 1,000 unique recipe rows selected from 3,443 strict-eligible source candidates.
- 623 unique canonical ingredients and 791 alias rows.
- 12,218 recipe–ingredient rows; 12,218 compact quantity tuples.
- 11,720 distinct ingredient-to-recipe reverse links.
- 30 curated demo recipes, all present in the selected 1,000.
- 0 selected ingredients with unclassified food types.
- 0 ingredient names with numeric/dash quantity prefixes.
- 0 recipe names with parenthetical/bracketed aliases or digits.
- 0 orphan recipe/ingredient foreign keys; reverse lookup pairs reconcile to the detailed relationship.
- 24 alias collision keys are retained for review, not auto-merged.
- 0 packet or packaged/prepared food-type categories.
- Validation status: PASS. See `audit/quality_report.json` and `audit/validation_checks.json`.

## Folder map

- `exports/`: recipes, ingredients, aliases, alias/type/unit convenience table, detailed and compact relationships, reverse lookup, type/unit summary, and demo shortlist.
- `audit/`: quality report, rejection log, alias collisions, and validation checks.
- `docs/`: schema and this handoff.
- `dev/`: temporary diagnostics and logs.
- `run_all.py`: complete reproducible rebuild.

## Rules and caveats

1. Translated fields only; Devanagari records are deferred to the Hindi upgrade.
2. Recipe names remove bracketed/parenthetical alternatives and redundant suffixes. IDs are dataset-version-local.
3. Mixed fractions and dash-prefixed quantities are normalized for parsing; original raw text is retained.
4. Source parenthetical aliases are preserved, but ambiguous aliases are not automatically merged.
5. Ingredient types use source text, transparent keyword rules, and selected glossary cross-checks. `classification_source` marks whether an ingredient was individually web-glossary cross-checked or assigned by source text/curated rules.
6. Suggested units are hints, not conversion rules. Inventory deductions need a validated quantity parser, ingredient-specific conversions, and tests.
7. Cuisine/course/diet/instructions/URLs are retained from source, not invented.
8. The legacy analysis folders are archived, not deleted; `data/processed/` and the original source ZIP were not changed.

## Before Supabase import

- Inspect `audit/quality_report.json`; require `validation_status: PASS`.
- Sample at least 50 raw ingredient segments against `recipe_ingredients.csv`, especially fractions, aliases, and prep notes.
- Review `audit/alias_collisions.csv` before implementing pantry ingredient matching.
- Verify schema constraints and foreign keys in the database seed script.
