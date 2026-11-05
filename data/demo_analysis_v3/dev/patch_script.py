from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
old='''    def quality_score(r):
        s=r["source"]
        return (int(bool(clean(s.get("URL",""))))*3 + int(bool(clean(s.get("TranslatedInstructions",""))))*3
                + int(len(r["recipe_name"])<=38)*2 + int(r["total"]<=90)*2
                + int(4<=len(r["ingredients"])<=18)*2
                + int(bool(clean(s.get("Cuisine","")))) + int(bool(clean(s.get("Course","")))))'''
new='''    def quality_score(r):
        s=r["source"]
        n=key(r["recipe_name"])
        popular_terms=[key(x[0]) for x in FAMOUS]
        simple_dish=any(n == term or n.startswith(term+" recipe") or n.startswith(term+" ") for term in popular_terms if term)
        fusion_penalty=any(term in n for term in ["pizza","pasta","soup","muesli","pinwheel","galette","momo","salad","pudding","trifle","barfi","peanut butter chicken"])
        return (int(bool(clean(s.get("URL",""))))*3 + int(bool(clean(s.get("TranslatedInstructions",""))))*3
                + int(len(r["recipe_name"])<=38)*3 + int(r["total"]<=90)*2
                + int(4<=len(r["ingredients"])<=18)*2
                + int(bool(clean(s.get("Cuisine","")))) + int(bool(clean(s.get("Course",""))))
                + int(simple_dish)*12 - int(fusion_penalty)*10)'''
if old not in s: raise SystemExit("score block not found")
s=s.replace(old,new)
old2='''        for p in patterns:
            pk=key(p)
            exact=[(rid,r) for nk,(rid,r) in norm_to_r.items() if nk==pk or nk.startswith(pk+" ") or pk in nk]
            if exact:
                exact.sort(key=lambda pair:(len(pair[1]["recipe_name"]),-pair[1]["score"]))
                found=exact[0]; break'''
new2='''        for p in patterns:
            pk=key(p)
            exact=[]
            for nk,(rid,r) in norm_to_r.items():
                if not (nk==pk or nk.startswith(pk+" ")):
                    continue
                if any(bad in nk for bad in ["peanut butter chicken","pizza","pasta","soup","muesli","pinwheel","sandwich","barfi","pudding","trifle","salad","momo","galette"]):
                    continue
                exact.append((rid,r))
            if exact:
                exact.sort(key=lambda pair:(len(pair[1]["recipe_name"]),-pair[1]["score"]))
                found=exact[0]; break'''
if old2 not in s: raise SystemExit("demo matcher block not found")
s=s.replace(old2,new2)
p.write_text(s,encoding="utf-8")
print("patched")
