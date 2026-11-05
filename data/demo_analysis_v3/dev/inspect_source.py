import zipfile, pandas as pd, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\IndianFoodDatasetCSV.csv.zip"
df=pd.read_csv(p,compression="zip",dtype=str,keep_default_na=False)
print("SHAPE",df.shape)
print("SAMPLE",df[["TranslatedRecipeName","TranslatedIngredients","TotalTimeInMins","Cuisine","Course","Diet","TranslatedInstructions","URL"]].head(3).to_json(orient="records",force_ascii=False))
for c in ["Cuisine","Course","Diet"]:
 print(c,json.dumps(df[c].value_counts().head(30).to_dict(),ensure_ascii=False))
print("times",df["TotalTimeInMins"].value_counts().head(10).to_dict())
