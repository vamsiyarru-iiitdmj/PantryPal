"""Build PantryPal's app-ready recipe and ingredient data from the source ZIP.

Usage (from this folder):
    python build_recipe_data.py
    python build_recipe_data.py --run-tests

The input archive is never modified.  Outputs are deterministic CSV/JSON files in
data/processed/ and are designed to seed the Step 1 recipe/catalog tables.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


SOURCE_FILE = Path("IndianFoodDatasetCSV.csv.zip")
OUTPUT_DIR = Path("data/processed")

RECIPE_COLUMNS = [
    "recipe_id", "recipe_name", "prep_time_min", "cook_time_min", "total_time_min",
    "servings", "cuisine", "course", "diet", "specific_diet", "source_diet", "instructions", "url",
]

UNIT_ALIASES = {
    "g": "g", "gram": "g", "grams": "g", "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "ml": "ml", "milliliter": "ml", "milliliters": "ml", "l": "l", "litre": "l", "litres": "l",
    "liter": "l", "liters": "l", "cup": "cup", "cups": "cup", "tbsp": "tbsp", "tablespoon": "tbsp",
    "tablespoons": "tbsp", "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp", "ounce": "oz",
    "ounces": "oz", "oz": "oz", "pound": "lb", "pounds": "lb", "lb": "lb", "lbs": "lb",
    "clove": "clove", "cloves": "clove", "piece": "piece", "pieces": "piece", "slice": "slice",
    "slices": "slice", "sprig": "sprig", "sprigs": "sprig", "bunch": "bunch", "bunches": "bunch",
    "inch": "inch", "inches": "inch", "can": "can", "cans": "can", "packet": "packet", "packets": "packet",
}

UNIT_DIMENSIONS = {
    "g": "mass", "kg": "mass", "oz": "mass", "lb": "mass",
    "ml": "volume", "l": "volume", "cup": "volume", "tbsp": "volume", "tsp": "volume",
    "clove": "count", "piece": "count", "slice": "count", "sprig": "count", "bunch": "count",
    "inch": "length", "can": "count", "packet": "count",
}

# This is an explainable seed taxonomy, not a nutritional claim.  Unclassified
# values are intentionally retained for frequency-ordered human review.
CATEGORY_RULES = [
    ("Meat & Seafood", {"chicken", "mutton", "lamb", "beef", "pork", "fish", "prawn", "shrimp", "crab", "maach", "anchovy", "tuna", "salmon", "sardine", "keema"}),
    ("Dairy & Eggs", {"milk", "curd", "yogurt", "yoghurt", "cream", "cheese", "paneer", "butter", "ghee", "buttermilk", "hung curd", "khoya", "mawa", "egg", "eggs"}),
    ("Oils & Fats", {"oil", "olive oil", "mustard oil", "sunflower oil", "coconut oil", "sesame oil", "vegetable oil", "nutralite classic spread"}),
    ("Vegetables", {"onion", "tomato", "potato", "carrot", "cabbage", "spinach", "peas", "bell pepper", "capsicum", "brinjal", "eggplant", "okra", "karela", "gourd", "pumpkin", "ash gourd", "white pumpkin", "kaddu", "beetroot", "cauliflower", "broccoli", "mushroom", "radish", "mooli", "turnip", "beans", "corn", "mixed vegetables", "bok choy", "chilli", "chillies", "green chili", "garlic", "ginger", "cucumber", "zucchini", "leek", "celery", "drumstick", "sorrel", "yam", "plantain", "bhindi", "shallots", "iceberg lettuce", "lettuce", "colocasia", "tindora", "gawar phali", "amaranth", "jalapeno", "jalapenos"}),
    ("Fruits", {"mango", "banana", "apple", "orange", "lemon", "lime", "pineapple", "grape", "guava", "papaya", "pomegranate", "watermelon", "coconut", "tamarind", "jackfruit", "avocado", "kokum", "amla", "fruit", "cherry", "cherries", "prune", "prunes", "cranberry", "cranberries", "blueberry", "blueberries", "apricot", "apricots", "kiwi", "berry", "berries", "strawberry", "strawberries", "olive", "olives", "dates", "fig"}),
    ("Herbs", {"coriander leaves", "coriander", "fresh herbs", "mint", "curry leaves", "basil", "oregano", "thyme", "rosemary", "parsley", "dill", "fenugreek leaves", "methi leaves", "kasuri methi", "bay leaf", "tulsi", "rose petals", "lemongrass", "mixed herbs"}),
    ("Spices & Seasonings", {"salt", "pepper", "peppercorn", "peppercorns", "black peppercorns", "turmeric", "cumin", "coriander powder", "chilli powder", "garam masala", "mustard seeds", "mustard", "asafoetida", "asafetida", "hing", "fennel", "cardamom", "cinnamon", "clove", "nutmeg", "saffron", "amchur", "masala", "paprika", "vanilla", "baking powder", "baking soda", "methi seeds", "ajwain", "star anise", "kalonji", "mace", "rye", "italian seasoning", "stone flowers", "fenugreek", "cooking soda", "kala jeera"}),
    ("Pulses & Legumes", {"dal", "lentil", "lentils", "chickpea", "chana", "urad", "moong", "rajma", "beans", "toor", "arhar", "peas", "soya", "soy", "tofu", "gram"}),
    ("Grains & Flours", {"rice", "flour", "atta", "maida", "sooji", "suji", "barley", "jowar", "ragi", "wheat", "semolina", "rava", "semiya", "oats", "muesli", "sabudana", "quinoa", "millet", "vermicelli", "poha", "besan", "corn flour"}),
    ("Nuts & Seeds", {"cashew", "almond", "badam", "peanut", "walnut", "pistachio", "nuts", "mixed nuts", "phool makhana", "sesame", "flax", "chia", "poppy", "melon seeds", "sunflower seeds", "raisins", "dry fruits", "tahini"}),
    ("Bakery & Pasta", {"bread", "bun", "baguette", "oreo biscuits", "marie biscuit", "puff pastry sheet", "tortilla", "pasta", "noodles", "idli", "dosa", "pizza base", "bread crumbs", "yeast"}),
    ("Sweeteners", {"sugar", "jaggery", "honey", "syrup", "molasses", "chocolate", "dark chocolate", "chocolate chips", "white chocolate", "nutella", "gulkand"}),
    ("Liquids", {"water", "juice", "stock", "broth", "vinegar", "wine", "tamarind water", "coconut milk", "ice", "ice cubes"}),
    ("Packaged & Prepared", {"ketchup", "sauce", "paste", "puree", "pickle", "gelatin", "mayonnaise", "jam", "chutney", "papad", "badi", "wadi", "tabasco", "sev", "boondi", "powder", "mix", "granules", "extract"}),
]

STAPLE_TERMS = {"salt", "water", "oil", "sunflower oil", "mustard oil", "vegetable oil", "ghee", "turmeric powder"}


@dataclass(frozen=True)
class ParsedIngredient:
    raw_text: str
    quantity_raw: str | None
    unit_raw: str | None
    unit: str | None
    ingredient_name: str
    aliases: tuple[str, ...]
    prep_note: str | None
    is_optional: bool


def clean_text(value: object) -> str:
    """Normalise whitespace without altering the semantic text."""
    return re.sub(r"\s+", " ", str(value or "").replace("\u00a0", " ")).strip()


def norm_key(value: str) -> str:
    value = clean_text(value).casefold()
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    value = re.sub(r"\b(the|fresh|whole)\b", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value.endswith("leaves") and len(value) > 6:
        value = value[:-6] + "leaf"
    elif value.endswith("ies") and len(value) > 4:
        value = value[:-3] + "y"
    elif value.endswith("oes") and len(value) > 4:
        value = value[:-2]
    elif value.endswith("s") and not value.endswith("ss") and len(value) > 3:
        value = value[:-1]
    return value


def split_outside_parentheses(text: str, delimiter: str = ",") -> list[str]:
    parts, current, depth = [], [], 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == delimiter and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return [part for part in parts if part]


def split_note(text: str) -> tuple[str, str | None]:
    """Split the first hyphen separator, retaining numeric ranges such as 1-1/2."""
    match = re.search(r"\s+-\s+", text)
    if not match:
        return text.strip(), None
    return text[:match.start()].strip(), text[match.end():].strip() or None


NUMBER = r"(?:\d+(?:\.\d+)?|[¼½¾])"
# Handles simple fractions, mixed fractions (1-1/2), additive quantities
# (1+1/3, 1/2 + 1/2), and ranges without mistaking them for ingredient names.
QUANTITY_ATOM = rf"{NUMBER}(?:\s*/\s*{NUMBER})?"
QUANTITY_RE = re.compile(
    rf"^(?P<quantity>(?:\d+\s*-\s*{QUANTITY_ATOM}|{QUANTITY_ATOM}(?:\s*\+\s*{QUANTITY_ATOM})?)(?:\s+to\s+{QUANTITY_ATOM})?|a\s+(?:pinch|handful)|few)\s+",
    re.IGNORECASE,
)


def extract_aliases(name: str) -> tuple[str, tuple[str, ...]]:
    aliases: list[str] = []
    for group in re.findall(r"\(([^()]*)\)", name):
        for alias in re.split(r"\s*/\s*|\s+or\s+|\s*,\s*", group, flags=re.IGNORECASE):
            alias = clean_text(alias)
            if alias and len(alias) <= 60 and not re.search(r"\b(such as|optional|split|cut|chopped|cooked)\b", alias, re.I):
                aliases.append(alias)
    primary = clean_text(re.sub(r"\([^()]*\)", " ", name))
    return primary, tuple(dict.fromkeys(aliases))


def parse_ingredient(raw_text: str) -> ParsedIngredient:
    raw_text = clean_text(raw_text)
    main, prep_note = split_note(raw_text)
    # Some source rows omit the hyphen before usage notes.
    note_match = re.search(r"\s+(to taste|as per taste|as per use|as required|as needed)$", main, re.I)
    if note_match:
        prep_note = prep_note or note_match.group(1)
        main = main[:note_match.start()].strip()

    quantity_raw = unit_raw = unit = None
    if norm_key(main) in {"as per taste", "as per use", "to taste", "as required", "as needed"}:
        return ParsedIngredient(raw_text, None, None, None, "Unparsed ingredient fragment", (), main, bool(re.search(r"\boptional\b", raw_text, re.I)))

    # Quantity-only fragments occasionally occur in the source after splitting
    # malformed comma-separated ingredient strings. Keep the row for audit, but
    # never promote a bare number/fraction to a canonical food ingredient.
    if re.fullmatch(r"(?:\d+(?:\s*[-+]\s*\d+)?(?:\s*/\s*\d+)?(?:\s*\+\s*\d+(?:\s*/\s*\d+)?)?|[¼½¾])", main):
        return ParsedIngredient(raw_text, main, None, None, "Unparsed ingredient fragment", (), prep_note, bool(re.search(r"\boptional\b", raw_text, re.I)))

    quantity_match = QUANTITY_RE.match(main)
    if quantity_match:
        quantity_raw = clean_text(quantity_match.group("quantity"))
        main = main[quantity_match.end():].strip()

    # Source translations sometimes say "small teaspoon" or "large cup".
    # Treat the size word as part of the measurement, not as an ingredient.
    compound_match = re.match(r"^(small|medium|large|big)\s+(teaspoons?|tablespoons?|cups?|spoons?)\b\s*", main, re.I)
    if compound_match:
        unit_raw = clean_text(compound_match.group(0)).strip()
        size_word, unit_word = compound_match.group(1).casefold(), compound_match.group(2).casefold()
        if unit_word.startswith("spoon"):
            unit = "tsp" if size_word == "small" else "tbsp"
        else:
            unit = UNIT_ALIASES[unit_word]
        main = main[compound_match.end():].strip()
    else:
        # A word such as "cloves" can be a measurement ("2 cloves garlic") or
        # the ingredient itself ("1 Cloves (Laung)"). Consume it as a unit only
        # when meaningful ingredient text remains after the unit.
        unit_match = re.match(r"^([A-Za-z]+)\b\s*", main)
        if unit_match:
            candidate = unit_match.group(1).casefold()
            remainder = main[unit_match.end():].strip()
            remainder_name, _ = extract_aliases(remainder)
            if candidate in UNIT_ALIASES and remainder_name and norm_key(remainder_name):
                unit_raw = unit_match.group(1)
                unit = UNIT_ALIASES[candidate]
                main = remainder

    ingredient_name, aliases = extract_aliases(main)
    ingredient_name = ingredient_name or clean_text(re.sub(r"\([^()]*\)", " ", main)) or raw_text
    ingredient_name = re.sub(r"[\s\-–—,;:]+$", "", ingredient_name).strip()
    if not norm_key(ingredient_name):
        if aliases:
            ingredient_name = aliases[0]
            aliases = tuple(alias for alias in aliases if norm_key(alias) != norm_key(ingredient_name))
        else:
            ingredient_name = "Unparsed ingredient fragment"
    optional = bool(re.search(r"\boptional\b", raw_text, flags=re.I))
    return ParsedIngredient(raw_text, quantity_raw, unit_raw, unit, ingredient_name, aliases, prep_note, optional)


def classify_ingredient(name: str, alternatives: Iterable[str] = ()) -> tuple[str, str, str]:
    keys = [norm_key(name)] + [norm_key(value) for value in alternatives if norm_key(value)]
    # Prefer specific ingredient phrases and use observed aliases as evidence.
    # This helps classify regional names when a parenthetical English alias exists.
    matches: list[tuple[int, str]] = []
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            keyword_key = norm_key(keyword)
            if not keyword_key:
                continue
            if any(re.search(rf"\b{re.escape(keyword_key)}\b", key) for key in keys):
                matches.append((len(keyword_key), category))
    if matches:
        category = sorted(matches, key=lambda item: item[0], reverse=True)[0][1]
        mass_categories = {
            "Meat & Seafood", "Dairy & Eggs", "Vegetables", "Fruits", "Herbs",
            "Spices & Seasonings", "Pulses & Legumes", "Grains & Flours",
            "Nuts & Seeds", "Bakery & Pasta", "Sweeteners",
        }
        dimension = "volume" if category in {"Liquids", "Oils & Fats"} else ("mass" if category in mass_categories else "count")
        return category, "keyword_rule", dimension
    return "Other / needs review", "unclassified", "mass"


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, item: str) -> str:
        self.parent.setdefault(item, item)
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[right] = left


def load_and_clean(source: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    raw = pd.read_csv(source, compression="zip", dtype=str, keep_default_na=False)
    raw_rows = len(raw)
    for column in ["PrepTimeInMins", "CookTimeInMins", "TotalTimeInMins", "Servings"]:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")
    required = ["TranslatedRecipeName", "TranslatedIngredients"]
    blank_mask = raw[required].apply(lambda col: col.astype(str).str.strip().eq("")).any(axis=1)
    # This source labels these fields "Translated", but 525 rows still contain
    # Devanagari text.  Keep the requested English/romanized release clean and
    # put those rows in the reject log for the later Hindi-language upgrade.
    devanagari_mask = raw[["TranslatedRecipeName", "TranslatedIngredients", "TranslatedInstructions"]].apply(
        lambda col: col.astype(str).str.contains(r"[\u0900-\u097F]", regex=True, na=False)
    ).any(axis=1)
    invalid_numeric = (raw[["PrepTimeInMins", "CookTimeInMins", "TotalTimeInMins", "Servings"]] < 0).any(axis=1) | raw["Servings"].isna()
    reject_mask = blank_mask | devanagari_mask | invalid_numeric
    rejects = raw.loc[reject_mask].copy()
    rejects["reject_reason"] = ""
    rejects.loc[blank_mask, "reject_reason"] += "missing_translated_recipe_or_ingredients;"
    rejects.loc[devanagari_mask, "reject_reason"] += "non_english_translated_content_deferred_to_hindi_upgrade;"
    rejects.loc[invalid_numeric, "reject_reason"] += "invalid_time_or_servings;"
    clean = raw.loc[~reject_mask].copy()
    clean["_recipe_key"] = clean["TranslatedRecipeName"].map(norm_key)
    duplicate_mask = clean.duplicated("_recipe_key", keep="first")
    duplicate_rejects = clean.loc[duplicate_mask].copy()
    duplicate_rejects["reject_reason"] = "duplicate_translated_recipe_name;"
    rejects = pd.concat([rejects, duplicate_rejects], ignore_index=True)
    clean = clean.loc[~duplicate_mask].copy()
    clean["recipe_id"] = range(1, len(clean) + 1)
    def base_diet(value: str) -> str:
        label = clean_text(value).casefold()
        if "non veget" in label or "non-veget" in label or "nonveget" in label:
            return "non_vegetarian"
        if "eggetarian" in label:
            return "eggetarian"
        if "veget" in label or "vegan" in label:
            return "vegetarian"
        return "unknown"
    clean["diet"] = clean["Diet"].map(base_diet)
    plain_diets = {"vegetarian", "non vegeterian", "non vegetarian", "non-vegetarian", "eggetarian", "vegan"}
    clean["specific_diet"] = clean["Diet"].where(~clean["Diet"].str.casefold().isin(plain_diets), "")
    stats = {"source_rows": raw_rows, "accepted_recipes": len(clean), "rejected_recipes": len(rejects)}
    return clean, rejects, stats


def parse_all_ingredients(clean: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in clean.itertuples(index=False):
        for position, segment in enumerate(split_outside_parentheses(row.TranslatedIngredients), start=1):
            parsed = parse_ingredient(segment)
            records.append({
                "recipe_id": row.recipe_id, "ingredient_position": position, "raw_text": parsed.raw_text,
                "quantity_raw": parsed.quantity_raw or "", "unit_raw": parsed.unit_raw or "", "unit": parsed.unit or "",
                "unit_dimension": UNIT_DIMENSIONS.get(parsed.unit or "", "unspecified"),
                "ingredient_name_raw": parsed.ingredient_name, "ingredient_key": norm_key(parsed.ingredient_name),
                "aliases_raw": " | ".join(parsed.aliases), "prep_note": parsed.prep_note or "",
                "is_optional": parsed.is_optional,
            })
    return pd.DataFrame(records)


def build_catalog(parsed: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Source parentheses are useful aliases, but they occasionally conflict
    # (e.g., a transliteration may be reused for a different flour).  Canonical
    # identity therefore uses a normalized primary name only; aliases are saved
    # as evidence instead of being transitively merged into false identities.
    display_names = parsed.groupby("ingredient_key")["ingredient_name_raw"].agg(
        lambda values: Counter(map(clean_text, values)).most_common(1)[0][0]
    ).to_dict()
    parsed["canonical_key"] = parsed["ingredient_key"]
    parsed["canonical_name"] = parsed["canonical_key"].map(display_names)
    catalog_rows, alias_rows = [], []
    for ingredient_id, (key, group) in enumerate(parsed.groupby("canonical_key", sort=True), start=1):
        name = clean_text(group["canonical_name"].iloc[0])
        aliases = set(group["ingredient_name_raw"].map(clean_text))
        aliases.update(alias.strip() for joined in group["aliases_raw"] for alias in joined.split(" | ") if alias.strip())
        aliases.add(name)
        category, method, default_dimension = classify_ingredient(name, aliases)
        catalog_rows.append({
            "ingredient_id": ingredient_id, "canonical_name": name, "canonical_key": key,
            "ingredient_type": category, "classification_method": method,
            "default_unit_dimension": default_dimension,
            "suggested_units": (
                "ml, l, cup, tbsp, tsp" if category in {"Liquids", "Oils & Fats"}
                else "g, kg, piece" if category in {"Vegetables", "Fruits", "Dairy & Eggs", "Meat & Seafood"}
                else "g, tsp, tbsp" if category in {"Herbs", "Spices & Seasonings", "Sweeteners"}
                else "g, kg, cup" if category in {"Pulses & Legumes", "Grains & Flours", "Nuts & Seeds"}
                else "g, ml, piece, packet"
            ),
            "is_staple": norm_key(name) in STAPLE_TERMS,
            "recipe_occurrences": int(len(group)), "recipe_count": int(group["recipe_id"].nunique()),
        })
        aliases = set(group["ingredient_name_raw"].map(clean_text))
        aliases.update(alias.strip() for joined in group["aliases_raw"] for alias in joined.split(" | ") if alias.strip())
        aliases.add(name)
        for alias in sorted(aliases, key=str.casefold):
            alias_rows.append({"ingredient_id": ingredient_id, "canonical_name": name, "alias": alias, "alias_key": norm_key(alias)})
    catalog = pd.DataFrame(catalog_rows)
    aliases = pd.DataFrame(alias_rows).drop_duplicates(["ingredient_id", "alias_key"])
    aliases = aliases[aliases["alias_key"].ne("")].copy()
    parsed = parsed.merge(catalog[["ingredient_id", "canonical_key", "canonical_name"]], on=["canonical_key", "canonical_name"], how="left")
    return catalog, aliases, parsed


def write_outputs(clean: pd.DataFrame, rejects: pd.DataFrame, parsed: pd.DataFrame, catalog: pd.DataFrame, aliases: pd.DataFrame, stats: dict[str, int]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    recipes = pd.DataFrame({
        "recipe_id": clean["recipe_id"], "recipe_name": clean["TranslatedRecipeName"].map(clean_text),
        "prep_time_min": clean["PrepTimeInMins"].astype("Int64"), "cook_time_min": clean["CookTimeInMins"].astype("Int64"),
        "total_time_min": clean["TotalTimeInMins"].astype("Int64"), "servings": clean["Servings"].astype("Int64"),
        "cuisine": clean["Cuisine"].map(clean_text), "course": clean["Course"].map(clean_text),
        "diet": clean["diet"], "specific_diet": clean["specific_diet"].map(clean_text),
        "source_diet": clean["Diet"].map(clean_text),
        "instructions": clean["TranslatedInstructions"].map(clean_text), "url": clean["URL"].map(clean_text),
    })[RECIPE_COLUMNS]
    recipes.to_csv(OUTPUT_DIR / "recipes_clean.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    rejects.to_csv(OUTPUT_DIR / "recipe_rejects.csv", index=False)
    catalog.to_csv(OUTPUT_DIR / "ingredients.csv", index=False)
    aliases.to_csv(OUTPUT_DIR / "ingredient_aliases.csv", index=False)
    recipe_ingredients = parsed[["recipe_id", "ingredient_position", "ingredient_id", "canonical_name", "quantity_raw", "unit", "unit_dimension", "prep_note", "is_optional", "raw_text"]].copy()
    recipe_ingredients.to_csv(OUTPUT_DIR / "recipe_ingredients.csv", index=False)
    # Keep malformed fragments in the detailed audit table, but do not advertise
    # them as usable ingredients in app-facing tuple/reverse-lookup exports.
    usable_ingredients = recipe_ingredients[recipe_ingredients["canonical_name"].ne("Unparsed ingredient fragment")].copy()
    usable_ingredients[["recipe_id", "canonical_name", "quantity_raw", "unit"]].to_csv(OUTPUT_DIR / "recipe_ingredient_tuples.csv", index=False)
    ingredient_recipes = usable_ingredients.merge(recipes[["recipe_id", "recipe_name", "cuisine", "course", "diet"]], on="recipe_id", how="left")
    ingredient_recipes[["ingredient_id", "canonical_name", "recipe_id", "recipe_name", "cuisine", "course", "diet"]].drop_duplicates().to_csv(OUTPUT_DIR / "ingredient_recipes.csv", index=False)
    unmatched = catalog[catalog["classification_method"].eq("unclassified")].sort_values(["recipe_occurrences", "canonical_name"], ascending=[False, True])
    unmatched.to_csv(OUTPUT_DIR / "ingredient_types_needing_review.csv", index=False)
    alias_collisions = aliases.groupby("alias_key")["ingredient_id"].nunique()
    alias_collisions = alias_collisions[alias_collisions > 1].reset_index(name="ingredient_candidates")
    aliases.merge(alias_collisions, on="alias_key", how="inner").sort_values(["ingredient_candidates", "alias_key"], ascending=[False, True]).to_csv(
        OUTPUT_DIR / "ingredient_alias_conflicts.csv", index=False
    )
    ingredient_with_type = recipe_ingredients.merge(catalog[["ingredient_id", "ingredient_type"]], on="ingredient_id", how="left")
    type_units = ingredient_with_type.groupby("ingredient_type", dropna=False).agg(
        ingredient_count=("ingredient_id", "nunique"),
        recipe_ingredient_rows=("ingredient_id", "size"),
        observed_units=("unit", lambda values: ", ".join(sorted({value for value in values if value}))),
        observed_unit_dimensions=("unit_dimension", lambda values: ", ".join(sorted({value for value in values if value and value != "unspecified"}))),
    ).reset_index().sort_values("ingredient_type")
    type_units.to_csv(OUTPUT_DIR / "ingredient_type_units.csv", index=False)
    pd.DataFrame(
        [{"unit": unit, "dimension": UNIT_DIMENSIONS[unit]} for unit in sorted(UNIT_DIMENSIONS)]
    ).to_csv(OUTPUT_DIR / "units.csv", index=False)
    suspicious = catalog[catalog["canonical_key"].isin({"long", "as per taste", "as per use", "take", "unparsed ingredient fragment"})].copy()
    suspicious["review_reason"] = "ambiguous_machine-translated ingredient phrase"
    suspicious.sort_values(["recipe_occurrences", "canonical_name"], ascending=[False, True]).to_csv(
        OUTPUT_DIR / "ingredient_parse_needs_review.csv", index=False
    )
    stats.update({
        "parsed_ingredient_rows": int(len(parsed)), "canonical_ingredients": int(len(catalog)), "aliases": int(len(aliases)),
        "typed_ingredients": int((catalog["classification_method"] != "unclassified").sum()),
        "unclassified_ingredients": int((catalog["classification_method"] == "unclassified").sum()),
        "mapped_ingredient_row_percent": round(float(parsed["ingredient_id"].notna().mean() * 100), 2),
    })
    with (OUTPUT_DIR / "data_quality_report.json").open("w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)
    if not (OUTPUT_DIR / "README.md").exists():
        (OUTPUT_DIR / "README.md").write_text(
        "# PantryPal cleaned recipe data\n\n"
        "Generated by `build_recipe_data.py`. Source ZIP remains unchanged.\n\n"
        "- `recipes_clean.csv`: translated recipe catalog and app filters.\n"
        "- `ingredients.csv`: canonical ingredient catalog, category seed, and staple flag.\n"
        "- `ingredient_aliases.csv`: observed translated names and parenthetical aliases.\n"
        "- `recipe_ingredients.csv`: parsed recipe-to-ingredient rows.\n"
        "- `recipe_ingredient_tuples.csv`: lean recipe / quantity / ingredient relation.\n"
        "- `ingredient_recipes.csv`: reverse ingredient-to-recipe lookup.\n"
        "- `ingredient_types_needing_review.csv`: conservative category exceptions, sorted by use.\n"
        "- `ingredient_alias_conflicts.csv`: aliases attached to multiple ingredients; review before mapping them at runtime.\n"
        "- `ingredient_type_units.csv` and `units.csv`: units observed in the source, grouped by ingredient type.\n"
        "- `ingredient_parse_needs_review.csv`: ambiguous machine-translated ingredient phrases retained for review.\n"
        "- `recipe_rejects.csv` and `data_quality_report.json`: reconciliation evidence.\n\n"
        "Category labels are seed metadata inferred from ingredient text; review the exceptions before enforcing category-specific inventory unit rules.\n",
        encoding="utf-8",
        )


def run_pipeline() -> dict[str, int]:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Expected source archive: {SOURCE_FILE.resolve()}")
    clean, rejects, stats = load_and_clean(SOURCE_FILE)
    parsed = parse_all_ingredients(clean)
    catalog, aliases, parsed = build_catalog(parsed)
    write_outputs(clean, rejects, parsed, catalog, aliases, stats)
    assert stats["source_rows"] == stats["accepted_recipes"] + stats["rejected_recipes"], "recipe reconciliation failed"
    assert parsed["ingredient_id"].notna().all(), "an ingredient was not mapped to a catalog row"
    return stats


def run_parser_tests() -> None:
    cases = {
        "1/2 teaspoon Cumin seeds (Jeera) - roasted": ("1/2", "tsp", "Cumin seeds", ("Jeera",), "roasted"),
        "2-1 / 2 cups rice - cooked": ("2-1 / 2", "cup", "rice", (), "cooked"),
        "6 to 8 Spinach Leaves (Palak)": ("6 to 8", None, "Spinach Leaves", ("Palak",), None),
        "Salt - to taste": (None, None, "Salt", (), "to taste"),
        "Sunflower Oil - as required": (None, None, "Sunflower Oil", (), "as required"),
        "500 grams Vellai Poosanikai (Ash gourd/White Pumpkin)": ("500", "g", "Vellai Poosanikai", ("Ash gourd", "White Pumpkin"), None),
        "1+1/3 cups Sugar": ("1+1/3", "cup", "Sugar", (), None),
        "1/2 + 1/2 cups Milk": ("1/2 + 1/2", "cup", "Milk", (), None),
        "1 Cloves (Laung)": ("1", None, "Cloves", ("Laung",), None),
        "Salt as per taste": (None, None, "Salt", (), "as per taste"),
        "1 small Spoon coriander powder": ("1", "tsp", "coriander powder", (), None),
        "2 Cloves (Laung) -": ("2", None, "Cloves", ("Laung",), None),
    }
    for text, expected in cases.items():
        actual = parse_ingredient(text)
        observed = (actual.quantity_raw, actual.unit, actual.ingredient_name, actual.aliases, actual.prep_note)
        assert observed == expected, f"{text!r}: expected {expected}, got {observed}"
    fragment = parse_ingredient("1/2")
    assert (fragment.quantity_raw, fragment.ingredient_name) == ("1/2", "Unparsed ingredient fragment")
    assert split_outside_parentheses("A (one, two), B") == ["A (one, two)", "B"]
    raw = pd.read_csv(SOURCE_FILE, compression="zip", dtype=str, keep_default_na=False)
    real_segments = []
    for value in raw["TranslatedIngredients"].head(200):
        real_segments.extend(split_outside_parentheses(value))
        if len(real_segments) >= 35:
            break
    assert len(real_segments) >= 30
    assert all(parse_ingredient(value).ingredient_name for value in real_segments[:35]), "real-row parser smoke test failed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-tests", action="store_true", help="Run parser tests before building outputs.")
    args = parser.parse_args()
    if args.run_tests:
        run_parser_tests()
        print("Parser tests passed.")
    result = run_pipeline()
    print(json.dumps(result, indent=2))
