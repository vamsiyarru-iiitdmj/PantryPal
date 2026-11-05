import pandas as pd,json,re
from pathlib import Path
b=Path(__file__).resolve().parent
ex=b/"exports"; au=b/"audit"
r=pd.read_csv(ex/"recipes_1000.csv",dtype=str,keep_default_na=False)
i=pd.read_csv(ex/"ingredients.csv",dtype=str,keep_default_na=False)
a=pd.read_csv(ex/"ingredient_aliases.csv",dtype=str,keep_default_na=False)
ri=pd.read_csv(ex/"recipe_ingredients.csv",dtype=str,keep_default_na=False)
t=pd.read_csv(ex/"recipe_ingredient_tuples.csv",dtype=str,keep_default_na=False)
rev=pd.read_csv(ex/"ingredient_recipes.csv",dtype=str,keep_default_na=False)
d=pd.read_csv(ex/"demo_30_selection.csv",dtype=str,keep_default_na=False)
checks={
"source_rows":6871,"recipe_rows":len(r),"unique_recipe_ids":int(r.recipe_id.nunique()),
"unique_recipe_names":int(r.recipe_name.str.lower().str.strip().nunique()),
"recipe_names_with_bracketed_aliases":int(r.recipe_name.str.contains(r"[()\[\]]",regex=True,na=False).sum()),
"recipe_names_with_digits":int(r.recipe_name.str.contains(r"\d",regex=True,na=False).sum()),
"ingredient_rows":len(i),"unique_ingredient_ids":int(i.ingredient_id.nunique()),
"ingredient_names_with_quantity_prefix":int(i.canonical_name.str.match(r"^\s*[–—-]?\s*\d",na=False).sum()),
"unclassified_ingredients":int(i.ingredient_type.eq("Other / needs review").sum()),
"ingredient_forms":i.ingredient_form.value_counts().to_dict(),
"alias_rows":len(a),"alias_collision_keys":int((a.groupby("alias_key").ingredient_id.nunique()>1).sum()),
"relation_rows":len(ri),"tuple_rows":len(t),"reverse_rows":len(rev),
"reverse_pairs_match_relation_pairs":bool(set(zip(rev.ingredient_id,rev.recipe_id))==set(zip(ri.ingredient_id,ri.recipe_id))),
"demo_rows":len(d),"demo_unique_recipe_ids":int(d.recipe_id.nunique()),
"demo_orphan_ids":int((~d.recipe_id.isin(r.recipe_id)).sum()),
"orphan_recipe_relations":int((~ri.recipe_id.isin(r.recipe_id)).sum()),
"orphan_ingredient_relations":int((~ri.ingredient_id.isin(i.ingredient_id)).sum()),
"packet_type_rows":int(i.ingredient_type.str.contains("packet",case=False,na=False).sum()),
"packaged_prepared_type_rows":int(i.ingredient_type.str.contains("packaged|prepared",case=False,na=False).sum()),
"missing_recipe_urls":int(r.url.str.strip().eq("").sum()),
"missing_instructions":int(r.instructions.str.strip().eq("").sum()),
}
checks["pass_core"] = (
 checks["recipe_rows"]==1000 and checks["unique_recipe_ids"]==1000 and checks["unique_recipe_names"]==1000
 and checks["recipe_names_with_bracketed_aliases"]==0 and checks["recipe_names_with_digits"]==0
 and checks["ingredient_names_with_quantity_prefix"]==0 and checks["unclassified_ingredients"]==0
 and checks["demo_rows"]==30 and checks["demo_unique_recipe_ids"]==30 and checks["demo_orphan_ids"]==0
 and checks["orphan_recipe_relations"]==0 and checks["orphan_ingredient_relations"]==0
 and checks["packet_type_rows"]==0 and checks["reverse_pairs_match_relation_pairs"]
)
(au/"validation_checks.json").write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding="utf-8")
report=json.loads((au/"quality_report.json").read_text(encoding="utf-8"))
report["validation"]=checks
report["validation_status"]="PASS" if checks["pass_core"] else "FAIL"
(au/"quality_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(checks,indent=2,ensure_ascii=False))
