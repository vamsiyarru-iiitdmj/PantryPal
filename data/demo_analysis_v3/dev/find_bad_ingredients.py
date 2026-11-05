import pandas as pd,sys
sys.stdout.reconfigure(encoding="utf-8")
b=r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\exports"
ri=pd.read_csv(b+r"\recipe_ingredients.csv",dtype=str,keep_default_na=False)
i=pd.read_csv(b+r"\ingredients.csv",dtype=str,keep_default_na=False)
print("BAD RELATIONS",ri[ri.ingredient_name.str.contains(r"^\d",regex=True)].head(15).to_string(index=False))
print("BAD INGREDIENTS",i[i.canonical_name.str.contains(r"^\d",regex=True)].head(15).to_string(index=False))
