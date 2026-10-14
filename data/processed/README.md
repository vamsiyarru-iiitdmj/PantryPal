# PantryPal Processed Recipe Data

Generated from `IndianFoodDatasetCSV.csv.zip` by `build_recipe_data.py`. The source archive is not modified. Field definitions are in [`schema.md`](schema.md).

## Version 1 — Initial processed export

The initial export introduced the translated recipe catalog and relationship tables. Its reconciliation report recorded 6,871 source rows, 5,990 accepted recipes, 881 rejected rows, 72,790 parsed ingredient rows, 1,805 canonical ingredient candidates, and 2,162 alias rows.

Initial known limitations identified during review:

- Some valid quantity expressions with `+` (for example `1+1/3` or `1/2 + 1/2`) were not reliably separated from ingredient names.
- A measurement word such as `cloves` could be mistaken for a unit even when cloves was the ingredient itself, creating malformed canonical names and many false alias conflicts.
- Category matching could classify an ingredient from a broad interior word (for example, a chilli powder name could be classified as a vegetable).
- Most non-liquid ingredient categories were incorrectly assigned `count` as the default unit dimension, and their suggested units were too generic.
- The recipe–ingredient relationship was exported in both a detailed table and a compact tuple table; both were retained in the initial export, but the detailed table was authoritative.

## Version 2 — Parser and classification review (2026-10-14)

Changes made to the reproducible pipeline before regenerating the exports:

- Expanded quantity parsing for mixed fractions and additive quantities while preserving the raw expression instead of forcing unsafe numeric conversion.
- Prevented count words such as `cloves` from being consumed as units when no ingredient text remains.
- Captured common usage notes such as `as per taste` even when the source omits a hyphen.
- Improved singularization for common `-leaves` and `-oes` forms.
- Changed category matching to consider full keyword phrases and prefer the most specific phrase, reducing interior-token false matches.
- Made broad unit dimensions category-aware and provided more relevant category-specific unit suggestions. These are still hints, not verified ingredient-specific conversions.
- Changed unexpected/unknown diet labels to `unknown` rather than silently assuming vegetarian.
- Added parser regression cases for additive quantities, parenthetical aliases, and usage notes.
- Added `schema.md` with field definitions, relationship meanings, and caveats.

**Latest regenerated counts (2026-10-14):** 6,871 source rows; 5,990 accepted recipes; 881 rejected rows; 72,790 ingredient rows; 1,728 canonical ingredient candidates; 2,044 alias rows; 1,385 classified candidates; 343 unclassified candidates; 100% of ingredient rows map to a catalog candidate. These are mechanical counts, not proof that every ingredient was parsed semantically correctly. Re-check `audit/data_quality_report.json` after any future rerun. Do not copy these counts or generated IDs into code as permanent constants; IDs are dataset-version-local.

## File guide

### Core exports for the app

- `recipes_clean.csv` — translated recipe metadata, instructions, URL, course, cuisine and diet labels.
- `ingredients.csv` — canonical ingredient candidates, inferred type, suggested units and occurrence counts.
- `ingredient_aliases.csv` — observed primary names and parenthetical aliases for lookup.
- `recipe_ingredients.csv` — authoritative detailed recipe–ingredient relationship, including quantity text, unit, preparation note and raw source segment.
- `ingredient_recipes.csv` — reverse lookup of recipes containing each usable ingredient. Recipe-level cuisine/course/diet details are available by joining to `recipes_clean.csv`.
- `units.csv` — unit names and broad dimensions only; no conversion factors are provided.

### Review and audit exports

These files are useful for validation and should not be loaded as independent app entities:

- `audit/ingredient_alias_conflicts.csv` — alias keys associated with multiple ingredient candidates; review before automatic alias resolution.
- `audit/ingredient_types_needing_review.csv` — ingredient candidates not assigned by the current category rules, sorted by frequency.
- `audit/ingredient_parse_needs_review.csv` — selected suspicious or ambiguous ingredient phrases.
- `audit/ingredient_type_units.csv` — summary of observed units grouped by category, not a per-ingredient unit mapping.
- `audit/recipe_rejects.csv` — source rows excluded from the accepted recipe catalog, with reasons.
- `audit/data_quality_report.json` — reconciliation and pipeline metrics.
- `analysis/analysis2.ipynb` — exploratory notebook.

## Important data caveats

- `quantity_raw` is text, not a standardized numeric amount. Inventory deduction must wait for a validated quantity parser and unit conversion model.
- A blank unit means no supported explicit unit was detected; it does not automatically mean pieces, grams, or zero.
- Category and suggested-unit fields are inferred seed metadata, not web-verified facts or hard constraints.
- Review high-frequency unclassified ingredients and alias conflicts before final app integration.
- The pipeline asserts source-row reconciliation and ingredient-catalog mapping, but those checks do not prove semantic correctness of every parsed ingredient. Continue sampling raw text against parsed outputs.

## Version 2.1 — Organized export (2026-10-14)

- Organized review files and the data quality report into `audit/`.
- Moved `analysis2.ipynb` into `analysis/`.
- Removed the duplicate `recipe_ingredient_tuples.csv` export because it overlapped with `recipe_ingredients.csv`.
- Removed `cuisine`, `course`, and `diet` from `ingredient_recipes.csv`; recipe details remain in `recipes_clean.csv`.
- Removed `canonical_name` from `recipe_ingredients.csv`; use `ingredient_id` to look up the name in `ingredients.csv`.
- Kept the main app CSVs in `data/processed/` and moved review-only outputs into `audit/`.

### Current main files

- `recipes_clean.csv` — recipe details, instructions, and source URL.
- `ingredients.csv` — ingredient catalog.
- `ingredient_aliases.csv` — alternate ingredient names for lookup.
- `recipe_ingredients.csv` — recipe ingredients, quantities, units, and preparation notes.
- `ingredient_recipes.csv` — reverse lookup of recipes containing each ingredient.
- `units.csv` — unit names and broad dimensions.
- `audit/` — quality report, rejected rows, and files needing review.
- `analysis/` — exploratory notebook.
