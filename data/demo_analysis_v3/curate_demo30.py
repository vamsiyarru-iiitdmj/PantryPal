import pandas as pd,json
from pathlib import Path
b=Path(__file__).resolve().parent
ex=b/"exports"
recipes=pd.read_csv(ex/"recipes_1000.csv",dtype=str,keep_default_na=False)
rel=pd.read_csv(ex/"recipe_ingredients.csv",dtype=str,keep_default_na=False)
choices=[
("Masala Dosa","Masala Dosa Recipe With Vegetable Filling"),
("Paneer Butter Masala","Paneer Butter Masala"),
("Palak Paneer","Palak Paneer"),
("Chicken Biryani","Ambur Star Chicken Biryani"),
("Vegetable Biryani","Vegetable Biryani Recipe With Chatpata Aloo"),
("Chicken Vindaloo","Chicken Vindaloo"),
("Coorg Chicken Curry","Coorg Koli Curry Recipe - Coorgi Chicken Curry"),
("Mangalore Fish Curry","Mangalore Fish Curry"),
("Chettinad Prawn Curry","Chettinad Prawn Curry"),
("Amritsari Fish Fry","Amritsari Fish Fry"),
("Amla Rasam","Amla Rasam"),
("Khaman Dhokla","Instant Khaman Dhokla"),
("Litti Chokha","Traditional Bihari Litti Chokha"),
("Pav Bhaji","Cheesy Pav Bhaji"),
("Angoori Rasmalai","Angoori Rasmalai"),
("Badam Halwa","Badam Halwa"),
("Karnataka Upma","Karnataka Steel Awarekai Upma"),
("Bihari Chana Dal Puri","Bihari Chana Daal Puri"),
("Kashmiri Chicken Pulao","Kashmiri Style Chicken Pulao"),
("Avarekalu Masala Vada","Avarekalu Masala Vada"),
("Carrot Methi Jowar Thepla","Carrot Methi Jowar Thepla"),
("Aloo Posto","Aloo Posto"),
("Avalakki Bella Usuli","Avalakki Bella Usuli"),
("Arbi Ajwain Sabzi","Arbi Ajwain Ki Sabzi"),
("Andhra Pepper Chicken","Andhra Pepper Chicken"),
("Amritsari Dal","Amritsari Dal"),
("Udupi Tomato Rasam","Udupi Tomato Rasam"),
("Drumstick Sambar","Coimbatore Style Drumstick Sambar"),
("Kashmiri Paneer Gravy","Kashmiri Paneer Gravy"),
("Sri Lankan Prawn Curry","Srilankan Prawn Curry")
]
byname={str(r["recipe_name"]).strip():r for _,r in recipes.iterrows()}
rows=[]
for display,exact in choices:
 if exact not in byname:
  raise SystemExit("Missing selected recipe: "+exact)
 r=byname[exact]
 rows.append({"recipe_id":r["recipe_id"],"demo_display_name":display,"match_name":exact,
              "reason":"Curated familiar regional dish; passed the strict ingredient and metadata quality gate."})
if len({r["recipe_id"] for r in rows})!=30: raise SystemExit("duplicate recipe ids")
pd.DataFrame(rows).to_csv(ex/"demo_30_selection.csv",index=False)
ids={int(r["recipe_id"]) for r in rows}
recipes[recipes.recipe_id.astype(int).isin(ids)].to_csv(ex/"demo_30_recipes.csv",index=False)
rel[rel.recipe_id.astype(int).isin(ids)].to_csv(ex/"demo_30_recipe_ingredients.csv",index=False)
report_path=b/"audit"/"quality_report.json"
report=json.loads(report_path.read_text(encoding="utf-8"))
report["demo_selection_method"]="Manually curated 30 familiar regional dishes from within the strict-clean selected 1,000; all chosen recipe IDs are included in recipes_1000.csv."
report["demo_recipe_names"]=[r["match_name"] for r in rows]
report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("CURATED_DEMO",len(rows))
print("\n".join(f'{r["demo_display_name"]}: {r["match_name"]}' for r in rows))
