import pandas as pd,re,sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\IndianFoodDatasetCSV.csv.zip"
df=pd.read_csv(p,compression="zip",dtype=str,keep_default_na=False)
for q in ["masala dosa","paneer butter masala","palak paneer","chole","rajma masala","dal tadka","aloo gobi","butter chicken","chicken biryani","vegetable biryani","samosa","pav bhaji","poha","upma","dhokla","rogan josh","fish curry","prawn masala","appam","pesarattu","lemon rice","tomato rice","gulab jamun","rice kheer","gajar halwa","raita","aloo paratha"]:
 pat=re.sub(r"[^a-z0-9 ]","",q.lower())
 vals=[]
 for n in df["TranslatedRecipeName"].tolist():
  nk=re.sub(r"[^a-z0-9 ]","",n.lower()).replace(" recipe","").strip()
  if nk==pat or nk.startswith(pat+" ") or nk.endswith(" "+pat):
   vals.append(n)
 print(q, "=>", vals[:8])
