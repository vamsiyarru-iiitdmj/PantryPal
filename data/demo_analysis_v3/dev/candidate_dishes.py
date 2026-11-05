import pandas as pd,re,sys
sys.stdout.reconfigure(encoding="utf-8")
p=r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\exports\recipes_1000.csv"
df=pd.read_csv(p,dtype=str,keep_default_na=False)
terms=["paneer","biryani","chicken curry","fish curry","fish fry","prawn curry","dal","chole","rajma","idli","dosa","sambar","rasam","poha","upma","dhokla","thepla","litti","pav bhaji","kheer","rasmalai","gulab jamun","halwa","pulao","paratha","vada","puri","chutney","vindaloo","appam","modak","jalebi","kadhi","thoran","avial","kurma","tikka","sabzi","kofta","pakora","puri","pongal","chicken 65","mutton","egg curry"]
bad=["pizza","pasta","soup","muesli","pinwheel","galette","momo","salad","pudding","trifle","macaroni","enchilada","cocktail","pesto","oriental twist","sandwich","noodle","burger","wrap"]
for term in terms:
 rows=[]
 for _,r in df.iterrows():
  n=r.recipe_name.lower()
  if term in n and not any(x in n for x in bad):
   rows.append(r.recipe_name)
 if rows: print(term+": "+" | ".join(rows[:5]))
