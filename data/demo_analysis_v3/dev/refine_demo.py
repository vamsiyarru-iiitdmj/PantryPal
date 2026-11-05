import pandas as pd,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
base=Path(__file__).resolve().parent
ex=base/"exports"
recipes=pd.read_csv(ex/"recipes_1000.csv",dtype=str,keep_default_na=False)
rel=pd.read_csv(ex/"recipe_ingredients.csv",dtype=str,keep_default_na=False)
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",str(s).lower())).strip()
# Mainstream dish targets; only choose from strict-clean selected catalogue.
targets=[
("Masala Dosa","masala dosa"),("Idli","idli"),("Sambar","sambar"),("Paneer Butter Masala","paneer butter masala"),
("Palak Paneer","palak paneer"),("Chole","chole masala"),("Rajma Masala","rajma masala"),("Dal Tadka","dal tadka"),
("Aloo Gobi","aloo gobi"),("Butter Chicken","butter chicken"),("Chicken Biryani","chicken biryani"),
("Vegetable Biryani","vegetable biryani"),("Samosa","samosa"),("Pav Bhaji","pav bhaji"),("Poha","poha"),
("Upma","upma"),("Dhokla","dhokla"),("Fish Curry","fish curry"),("Prawn Masala","prawn masala"),
("Appam","appam"),("Lemon Rice","lemon rice"),("Tomato Rice","tomato rice"),("Gulab Jamun","gulab jamun"),
("Rice Kheer","rice kheer"),("Gajar Halwa","gajar halwa"),("Raita","raita"),("Aloo Paratha","aloo paratha"),
("Pulao","pulao"),("Dal Makhani","dal makhani"),("Chicken Curry","chicken curry"),
("Tandoori Chicken","tandoori chicken"),("Matar Paneer","matar paneer"),("Malai Kofta","malai kofta"),
("Medu Vada","medu vada"),("Puri","puri"),("Thepla","thepla"),("Kadhi","kadhi"),("Pongal","pongal"),
("Rasam","rasam"),("Pesarattu","pesarattu"),("Misal Pav","misal pav"),("Litti Chokha","litti chokha"),
("Dahi Vada","dahi vada"),("Kadhi Pakora","kadhi pakora"),("Chicken 65","chicken 65"),
("Hyderabadi Biryani","hyderabadi biryani"),("Fish Fry","fish fry"),("Modak","modak"),("Jalebi","jalebi"),
("Besan Ladoo","besan ladoo"),("Shrikhand","shrikhand"),("Khandvi","khandvi"),("Handvo","handvo"),
("Puran Poli","puran poli"),("Baingan Bharta","baingan bharta"),("Bhindi Masala","bhindi masala"),
("Aloo Tikki","aloo tikki"),("Chana Masala","chana masala"),("Vegetable Kurma","vegetable kurma"),
("Vegetable Pulao","vegetable pulao"),("Rava Kesari","rava kesari"),("Payasam","payasam"),
("Chicken Chettinad","chicken chettinad"),("Kerala Fish Curry","kerala fish curry"),
("Mushroom Masala","mushroom masala"),("Egg Curry","egg curry"),("Egg Bhurji","egg bhurji"),
("Paratha","paratha"),("Pani Puri","pani puri"),("Bhel Puri","bhel puri"),("Dosa","dosa"),
("Kootu","kootu"),("Avial","avial"),("Thoran","thoran"),("Bisi Bele Bath","bisi bele bath"),
("Vada Pav","vada pav"),("Misal","misal"),("Pav","pav")
]
# avoid fusion variants for a plain-dish match where obvious
bad_phrases=["peanut butter chicken","pizza","pasta","soup","muesli","pinwheel","sandwich","barfi","pudding","trifle","ladoo with","salad","chips","lollipop","noodles","macaroni"]
names=[]
for _,r in recipes.iterrows():
 n=norm(r.recipe_name)
 names.append((int(r.recipe_id),r.recipe_name,n))
chosen=[]
used=set()
for display,phrase in targets:
 q=norm(phrase)
 matches=[]
 for rid,name,n in names:
  if rid in used: continue
  if n==q or n==q+" recipe" or n.startswith(q+" recipe "):
   score=0
  elif n.startswith(q+" "):
   extra=n[len(q):].strip()
   score=2+len(extra.split())
  elif " "+q+" " in " "+n+" " or n.endswith(" "+q):
   prefix=n.split(q)[0].strip()
   suffix=n.split(q,1)[1].strip()
   score=8+len(prefix.split())+len(suffix.split())
  else: continue
  if any(b in n for b in bad_phrases): score+=20
  # Prefer names without redundant translated title repeats.
  if " - " in name and norm(name.split(" - ")[0])==q: score-=1
  matches.append((score,len(name),rid,name))
 if matches:
  matches.sort()
  score,_,rid,name=matches[0]
  chosen.append({"recipe_id":rid,"demo_display_name":display,"match_name":name,
                 "reason":"Selected from the strict-clean 1,000; closest available match to a familiar dish."})
  used.add(rid)
# Broad but still recognizable Indian dishes to fill any gaps, all already quality checked.
fallback_targets=["Aam Ka Panna","Amla Rasam","Chicken Vindaloo","Avarekalu Tikki","Kashmiri Pulao","Vegetable Kurma","Rava Idli","Coconut Chutney","Green Chutney","Tomato Chutney","Coconut Rice","Curd Rice","Jeera Rice","Vegetable Fried Rice","Paneer Tikka","Hara Bhara Kabab","Kachori","Pakora","Onion Pakoda","Pesarattu","Ragi Dosa","Methi Thepla","Methi Malai Matar","Aloo Matar","Dal Palak","Baingan Bharta","Methi Paratha","Mysore Pak","Rasgulla","Sandesh","Payasam","Kozhukattai","Vegetable Stew","Prawn Curry","Chicken Korma","Mutton Curry","Chicken 65","Kathi Roll","Kachumber Salad","Dahi Puri","Sev Puri","Khichdi","Masala Khichdi","Lauki Kofta","Kadai Paneer","Shahi Paneer","Mushroom Curry","Tamarind Rice","Curd Rice","Vermicelli Upma","Kanda Poha"]
for q in fallback_targets:
 if len(chosen)>=30: break
 nq=norm(q)
 matches=[]
 for rid,name,n in names:
  if rid in used: continue
  if n==nq or n==nq+" recipe" or n.startswith(nq+" recipe "):
   score=0
  elif n.startswith(nq+" "):
   score=2+len(n[len(nq):].split())
  else: continue
  if any(b in n for b in bad_phrases): score+=20
  matches.append((score,len(name),rid,name))
 if matches:
  matches.sort()
  _,_,rid,name=matches[0]
  chosen.append({"recipe_id":rid,"demo_display_name":q,"match_name":name,
                 "reason":"Quality-passed fallback dish; selected to keep the demo culturally diverse."})
  used.add(rid)
# final fill with popular-ish short Indian recipes, not alphabetical first 30
if len(chosen)<30:
 for rid,name,n in sorted(names,key=lambda x:(len(x[2].split()),len(x[1]),x[1].lower())):
  if rid in used: continue
  if any(term in n for term in ["recipe","masala","dal","rice","curry","paneer","idli","dosa","paratha","chutney","sabzi","halwa","biryani","vada","pulao","roti","poha","upma","pakora","chole","rajma","sambar","rasam","kheer","pav","thoran","kootu","payasam"]):
   chosen.append({"recipe_id":rid,"demo_display_name":name,"match_name":name,
                  "reason":"Quality-passed familiar Indian dish used to complete demo diversity."})
   used.add(rid)
   if len(chosen)>=30: break
chosen=chosen[:30]
pd.DataFrame(chosen).to_csv(ex/"demo_30_selection.csv",index=False)
ids={d["recipe_id"] for d in chosen}
recipes[recipes.recipe_id.astype(int).isin(ids)].to_csv(ex/"demo_30_recipes.csv",index=False)
rel[rel.recipe_id.astype(int).isin(ids)].to_csv(ex/"demo_30_recipe_ingredients.csv",index=False)
print("DEMO_COUNT",len(chosen))
print(pd.DataFrame(chosen).to_string(index=False))
