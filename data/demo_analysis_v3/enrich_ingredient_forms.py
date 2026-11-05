import pandas as pd,re,json
from pathlib import Path
b=Path(__file__).resolve().parent
ex=b/"exports"
ingredients=pd.read_csv(ex/"ingredients.csv",dtype=str,keep_default_na=False)
aliases=pd.read_csv(ex/"ingredient_aliases.csv",dtype=str,keep_default_na=False)
def form(name,typ):
 n=str(name).lower()
 if typ=="Liquids" or any(x in n for x in ["juice","stock","broth","vinegar","water","milk","sauce","extract","syrup","wine"]): return "liquid"
 if any(x in n for x in ["powder","flour","ground ","masala","spice mix","baking soda","baking powder"]): return "powder_or_blend"
 if any(x in n for x in ["paste","puree"]): return "paste_or_puree"
 if any(x in n for x in ["dried","dry ","dehydrated","sun-dried","sun dried","kasuri"]): return "dried"
 if any(x in n for x in ["leaves","leaf","fresh ","chopped","grated","sliced"]): return "fresh_or_cut"
 if typ in {"Vegetables","Fruits","Meat & Seafood","Herbs"}: return "fresh_or_whole"
 return "whole_or_solid"
ingredients["ingredient_form"]=ingredients.apply(lambda r:form(r["canonical_name"],r["ingredient_type"]),axis=1)
ingredients["classification_source"]=ingredients["classification_method"].map(
 lambda method: "Indian ingredient glossaries cross-checked; see audit/quality_report.json"
 if method=="glossary_rule" else "Source text and curated keyword rules; not individually web-verified"
)
ingredients.to_csv(ex/"ingredients.csv",index=False)
aliases=aliases.merge(ingredients[["ingredient_id","ingredient_type","ingredient_form","classification_source","default_unit_dimension","suggested_units","observed_units"]],on="ingredient_id",how="left")
aliases.to_csv(ex/"ingredient_alias_type_units.csv",index=False)
# Update type-unit summary with the distribution of ingredient forms.
rows=[]
for typ,g in ingredients.groupby("ingredient_type"):
 rows.append({"ingredient_type":typ,"ingredient_count":int(len(g)),
  "default_unit_dimensions":" | ".join(sorted(set(g.default_unit_dimension))),
  "ingredient_forms":" | ".join(sorted(set(g.ingredient_form))),
  "suggested_units":"; ".join(sorted(set(g.suggested_units))),
  "observed_units_in_source":" | ".join(sorted({u for joined in g.observed_units for u in str(joined).split(" | ") if u}))})
pd.DataFrame(rows).to_csv(ex/"ingredient_type_units.csv",index=False)
print("ENRICHED",len(ingredients),"ingredients",len(aliases),"alias rows")
