# Schema notes — fresh analysis v3

## Primary tables

### \`recipes_1000.csv\`
One row per selected recipe. \`recipe_id\` is version-local; \`source_recipe_id\` retains the original source identifier. \`recipe_name\` is the cleaned translated name. Time values are minutes. \`diet\` is normalized to \`vegetarian\`, \`non_vegetarian\`, or \`eggetarian\`; \`specific_diet\` preserves labels such as high-protein vegetarian, gluten-free, or diabetic-friendly. Instructions and URLs come from the source.

### \`ingredients.csv\`
One row per canonical ingredient in the selected 1,000 recipes. \`ingredient_type\` is the broad food category (for example vegetables, spices, liquids, grains/flours, or dairy). \`ingredient_form\` is a separate form hint (liquid, powder/blend, paste/puree, dried, fresh/cut, fresh/whole, or whole/solid). \`suggested_units\` are practical UI choices, not conversions. \`observed_units\` lists units found in the source. \`classification_source\` states whether the classification came from source text/curated rules or a glossary cross-check.

### \`ingredient_aliases.csv\`
One row per canonical ingredient and alias. Parenthetical aliases are retained as evidence; ambiguous alias keys can point to multiple ingredient IDs. See \`audit/alias_collisions.csv\`.

### \`ingredient_alias_type_units.csv\`
Convenience join of each alias with its canonical ingredient's type, form, classification provenance, suggested units, and observed units.

### \`recipe_ingredients.csv\`
Authoritative many-to-many recipe–ingredient relationship. \`(recipe_id, ingredient_position)\` identifies a source position. Contains \`quantity_raw\`, normalized \`unit\` when detected, unit dimension, preparation notes, optionality, and original \`raw_text\`.

### \`recipe_ingredient_tuples.csv\`
Compact \`recipe_id, ingredient_id, quantity_raw, unit\` relationship.

### \`ingredient_recipes.csv\`
Reverse lookup, one row per selected ingredient–recipe pair. Join recipe IDs to \`recipes_1000.csv\` for cuisine, course, diet, instructions, time and URL.

### \`ingredient_type_units.csv\`
Summary by food type, including suggested units, forms and source-observed units. It is not a conversion table.

## Relationship model

\`\`\`
recipes_1000.recipe_id 1 ─── * recipe_ingredients.recipe_id
ingredients.ingredient_id 1 ─── * recipe_ingredients.ingredient_id
ingredients.ingredient_id 1 ─── * ingredient_aliases.ingredient_id
ingredients.ingredient_id 1 ─── * ingredient_recipes.ingredient_id
recipes_1000.recipe_id 1 ─── * ingredient_recipes.recipe_id
\`\`\`

## Inventory safety

- An empty unit means no supported explicit unit was detected, not zero or automatically pieces.
- Quantity text can contain ranges, fractions, additive expressions and vague amounts.
- Do not convert grams to pieces or volumes to mass without ingredient-specific conversion evidence.
- Do not auto-resolve alias collisions.
- Diet labels are source labels, not nutrition calculations or medical advice.
