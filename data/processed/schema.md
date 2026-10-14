# PantryPal Processed Data — Schema Reference

CSV files use UTF-8 with a header row. IDs belong to this generated dataset and may change when the source or cleaning rules change.

## Core files

### `recipes_clean.csv`
One row per accepted recipe. Includes `recipe_id`, `recipe_name`, preparation/cooking/total times, servings, cuisine, course, diet labels, instructions, and URL.

### `ingredients.csv`
One row per ingredient candidate. Includes `ingredient_id`, `canonical_name`, `canonical_key`, inferred `ingredient_type`, suggested unit metadata, staple flag, and occurrence counts.

### `ingredient_aliases.csv`
Maps observed names and aliases to `ingredient_id`. Review `audit/ingredient_alias_conflicts.csv` before relying on ambiguous aliases.

### `recipe_ingredients.csv`
One row per recipe–ingredient occurrence:
- `recipe_id`: recipe identifier matching `recipes_clean.csv`.
- `ingredient_position`: source order of the ingredient.
- `ingredient_id`: candidate identifier matching `ingredients.csv`.
- `quantity_raw`: quantity expression as text, not a standardized number.
- `unit`: recognized unit, if available.
- `unit_dimension`: broad dimension inferred for the unit.
- `prep_note`: preparation or usage note.
- `is_optional`: whether the source explicitly marks it optional.
- `raw_text`: original translated ingredient segment for review.

Use `ingredient_id` to retrieve the display name from `ingredients.csv`; `canonical_name` is not repeated in this table.

### `ingredient_recipes.csv`
Reverse lookup table with `ingredient_id`, `canonical_name`, `recipe_id`, and `recipe_name`. It answers which recipes contain an ingredient. Recipe cuisine, course, and diet fields are not duplicated here; join with `recipes_clean.csv` when needed.

### `units.csv`
Unit names and broad dimensions only. No conversion factors are included.

## Audit and analysis

Review files and the data quality report are in `audit/`. The exploratory notebook is in `analysis/`.

## Important notes

- Parsed ingredient rows are not proof that quantity or ingredient identity is correct; inspect `raw_text` during validation.
- Blank units do not mean zero, pieces, or grams.
- Suggested units and ingredient categories are inferred hints, not verified conversions or a strict food taxonomy.
- Validate quantity parsing and unit conversions before using recipe quantities for pantry stock deduction.
