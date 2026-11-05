import pandas as pd,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
b=Path(__file__).resolve().parent
ex=b/"exports"; au=b/"audit"
report=json.loads((au/"quality_report.json").read_text(encoding="utf-8"))
report["web_references"]=[
 {"title":"Indian spices glossary — Veg Recipes of India","url":"https://www.vegrecipesofindia.com/indian-spices-glossary-of-indian-spices-in-english-and-hindi/","use":"Cross-check common Indian spice names and regional-language aliases."},
 {"title":"Indian vegetables glossary — Veg Recipes of India","url":"https://www.vegrecipesofindia.com/glossary-indian-vegetables/","use":"Cross-check common vegetable names and regional-language equivalents."},
 {"title":"Indian pulses and legumes glossary — Veg Recipes of India","url":"https://www.vegrecipesofindia.com/glossary-of-legumes-lentils-in-english-and-hindi/","use":"Cross-check common pulse, lentil, and flour terminology."},
 {"title":"IndianFoodDatasetGeneration source README","url":"https://github.com/kanishk307/IndianFoodDatasetGeneration","use":"Verify source dataset provenance and translated field definitions."}
]
report["parsing_notes"]=[
 "Mixed fractions written as '1 1/2 cup' are normalized internally to the parser's '1-1/2' form; the original source segment is preserved in raw_text.",
 "Recipe names have parenthetical/bracketed aliases removed, redundant identical title repeats simplified, and a trailing 'Recipe' suffix removed where present.",
 "Any ingredient candidate whose parsed name still begins with a digit is rejected rather than included as an ingredient."
]
report["validation_file"]="audit/validation_checks.json"
(au/"quality_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
types=pd.read_csv(ex/"ingredients.csv",dtype=str,keep_default_na=False)
print("TYPES",json.dumps(types.ingredient_type.value_counts().to_dict(),ensure_ascii=False))
print("START_DIGIT",int(types.canonical_name.str.match(r"^\s*\d",na=False).sum()))
print("PACKET_CATEGORY",int(types.ingredient_type.str.contains("packet",case=False,na=False).sum()))
