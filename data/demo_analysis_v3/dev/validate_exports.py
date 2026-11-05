import pandas as pd,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
b=Path(__file__).resolve().parent/"exports"
r=pd.read_csv(b/"recipes_1000.csv",dtype=str,keep_default_na=False)
i=pd.read_csv(b/"ingredients.csv",dtype=str,keep_default_na=False)
a=pd.read_csv(b/"ingredient_aliases.csv",dtype=str,keep_default_na=False)
ri=pd.read_csv(b/"recipe_ingredients.csv",dtype=str,keep_default_na=False)
t=pd.read_csv(b/"recipe_ingredient_tuples.csv",dtype=str,keep_default_na=False)
rev=pd.read_csv(b/"ingredient_recipes.csv",dtype=str,keep_default_na=False)
d=pd.read_csv(b/"demo_30_selection.csv",dtype=str,keep_default_na=False)
checks={
"recipe_rows":len(r),"unique_recipe_ids":r.recipe_id.nunique(),"unique_recipe_names":r.recipe_name.str.lower().str.strip().nunique(),
"ingredient_rows":len(i),"unique_ingredient_ids":i.ingredient_id.nunique(),"alias_rows":len(a),
"relation_rows":len(ri),"tuple_rows":len(t),"reverse_rows":len(rev),"demo_rows":len(d),
"unclassified_ingredients":int(i.ingredient_type.eq("Other / needs review").sum()),
"numeric_or_symbol_names":int(r.recipe_name.str.fullmatch(r"[\W\d_]+",na=False).sum()),
"empty_ingredient_names":int(i.canonical_name.str.strip().eq("").sum()),
"orphan_recipe_relations":int((~ri.recipe_id.isin(r.recipe_id)).sum()),
"orphan_ingredient_relations":int((~ri.ingredient_id.isin(i.ingredient_id)).sum()),
"demo_orphan_ids":int((~d.recipe_id.isin(r.recipe_id)).sum()),
"packet_type_rows":int(i.ingredient_type.str.contains("packet",case=False,na=False).sum()),
"duplicate_alias_keys":int((a.groupby("alias_key").ingredient_id.nunique()>1).sum()),
}
print(json.dumps(checks,indent=2))
(Path(__file__).resolve().parent/"audit"/"validation_checks.json").write_text(json.dumps(checks,indent=2),encoding="utf-8")
