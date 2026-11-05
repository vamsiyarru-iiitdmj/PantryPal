# PantryPal recipe dataset — fresh analysis v3

This is a fresh, isolated rebuild from the unchanged source archive at the project root: `IndianFoodDatasetCSV.csv.zip`. The flawed legacy `data/Analysis` and `data/Analysis2` folders are archived under `data/archive_legacy_analysis/` for recovery. The older `data/processed/` folder is preserved untouched until the new exports are integrated.

## Validated snapshot

- 6,871 source rows; 3,443 strict-eligible recipes.
- 1,000 unique selected recipes; 30 curated demo recipes included in that 1,000.
- 623 canonical ingredients; 791 alias rows.
- 12,218 detailed recipe–ingredient rows and compact quantity tuples; 11,720 reverse ingredient–recipe pairs.
- 0 unclassified selected ingredients, quantity-prefixed ingredient names, parenthetical/bracketed recipe-name aliases, or orphan relationship keys.
- 24 alias collision keys retained for review; no packet or packaged/prepared ingredient-type categories.
- Validation: PASS. See `audit/quality_report.json` and `audit/validation_checks.json`.

## Folder map

- `run_all.py` — runs the full deterministic pipeline, enrichment, demo curation, and validation.
- `build_demo_dataset.py` — strict recipe selection, ingredient parsing/classification, and base exports.
- `enrich_ingredient_forms.py` — adds form and classification provenance fields.
- `curate_demo30.py` — selects the curated 30-recipe shortlist from the selected 1,000.
- `finalize_report.py`, `final_validation.py` — source references, metrics, and validation checks.
- `exports/recipes_1000.csv` — recipe metadata, translated instructions and URLs.
- `exports/demo_30_selection.csv`, `demo_30_recipes.csv`, `demo_30_recipe_ingredients.csv` — demo shortlist and its data.
- `exports/ingredients.csv` — canonical ingredient catalogue, food type/form, unit guidance, and classification provenance.
- `exports/ingredient_aliases.csv` — canonical names and observed parenthetical aliases.
- `exports/ingredient_alias_type_units.csv` — alias + food type/form + unit guidance convenience table.
- `exports/recipe_ingredients.csv` — detailed recipe-to-ingredient relationship with raw quantity/source segment.
- `exports/recipe_ingredient_tuples.csv` — compact recipe/ingredient/quantity relationship.
- `exports/ingredient_recipes.csv` — reverse lookup of all selected recipes containing each ingredient.
- `exports/ingredient_type_units.csv` — per-type suggested units, forms, and source-observed units.
- `audit/quality_report.json` — source/selection metrics, rules, references, limitations, and validation result.
- `audit/validation_checks.json` — explicit name, uniqueness, classification, and foreign-key checks.
- `audit/selection_rejections.csv` — rejected source rows and reasons.
- `audit/alias_collisions.csv` — alias keys linked to multiple canonical ingredients.
- `docs/schema.md`, `docs/HANDOFF.md` — schema and teammate handoff.
- `dev/` — temporary diagnostics and logs, separate from app-facing exports.

## Quality rules

- Use translated recipe names, ingredients, and instructions only; Devanagari records are deferred to a later upgrade.
- Recipe names are simplified by removing parenthetical/bracketed alternatives, repeated identical titles, and trailing `Recipe` suffixes. Duplicate normalized names are rejected.
- Mixed quantities such as `1 1/2 cup` and dash-prefixed quantities are normalized internally for parsing; the original source segment remains in `raw_text`.
- Selected recipes require usable translated instructions, reasonable time/serving metadata, cuisine/course labels, a known base diet, and fully classified ingredient identities.
- The food-type taxonomy does not contain a `packet` or `Packaged & Prepared` category.
- Cuisine, course, diet, times, instructions and URLs come from source fields, not invented values. Specific diet labels are preserved in `specific_diet`.
- Alias collisions are reported rather than silently merged.
- Suggested units are UI guidance, not conversion factors; quantity text is not yet safe for inventory arithmetic.

## Rebuild

Run from the project root:

```powershell
python data\demo_analysis_v3\run_all.py
```

Check that `audit/quality_report.json` reports `validation_status: PASS` before importing into Supabase.
