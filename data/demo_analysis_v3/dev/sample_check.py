import pandas as pd,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
b=Path(__file__).resolve().parent/"exports"
r=pd.read_csv(b/"recipes_1000.csv",dtype=str,keep_default_na=False)
print("PAREN_NAMES",r[r.recipe_name.str.contains(r"[()\[\]]",regex=True,na=False)].recipe_name.head(20).to_list())
print("SAMPLE_RECIPES",r[["recipe_name","total_time_min","cuisine","course","diet","specific_diet","url"]].head(10).to_json(orient="records",force_ascii=False))
i=pd.read_csv(b/"ingredients.csv",dtype=str,keep_default_na=False)
print("TYPES",i.ingredient_type.value_counts().to_dict())
print("ING_SAMPLE",i[["canonical_name","ingredient_type","suggested_units","observed_units"]].head(20).to_json(orient="records",force_ascii=False))
