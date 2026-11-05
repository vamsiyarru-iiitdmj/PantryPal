from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
needle="import pandas as pd\n"
if "sys.stdout.reconfigure(encoding=\"utf-8\")" not in s:
 s=s.replace(needle,needle+"\nsys.stdout.reconfigure(encoding=\"utf-8\")\n",1)
p.write_text(s,encoding="utf-8")
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\enrich_ingredient_forms.py")
s=p.read_text(encoding="utf-8")
s=s.replace('''ingredients["ingredient_form"]=ingredients.apply(lambda r:form(r["canonical_name"],r["ingredient_type"]),axis=1)
ingredients.to_csv(ex/"ingredients.csv",index=False)''','''ingredients["ingredient_form"]=ingredients.apply(lambda r:form(r["canonical_name"],r["ingredient_type"]),axis=1)
ingredients["classification_source"]=ingredients["classification_method"].map(
 lambda method: "Indian ingredient glossaries cross-checked; see audit/quality_report.json"
 if method=="glossary_rule" else "Source text and curated keyword rules; not individually web-verified"
)
ingredients.to_csv(ex/"ingredients.csv",index=False)''')
s=s.replace('''["ingredient_id","ingredient_type","ingredient_form","default_unit_dimension","suggested_units","observed_units"]''','''["ingredient_id","ingredient_type","ingredient_form","classification_source","default_unit_dimension","suggested_units","observed_units"]''')
p.write_text(s,encoding="utf-8")
print("UTF-8 output and classification provenance patched")
