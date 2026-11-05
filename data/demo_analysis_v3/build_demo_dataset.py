from __future__ import annotations
import csv, json, re, sys, shutil
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "IndianFoodDatasetCSV.csv.zip"
OUT = Path(__file__).resolve().parent
EXPORTS = OUT / "exports"
AUDIT = OUT / "audit"
DOCS = OUT / "docs"
for d in (EXPORTS, AUDIT, DOCS):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
import build_recipe_data as base

# Reviewed, source-grounded synonym expansions for common Indian ingredients.
# Parenthetical source aliases are retained separately as evidence.
MANUAL_TYPE_RULES = [
 ("Meat & Seafood", ["chicken","mutton","lamb","fish","prawn","shrimp","crab","egg","eggs","keema","meat","salmon","tuna","sardine"]),
 ("Dairy & Eggs", ["milk","curd","yogurt","yoghurt","cream","cheese","paneer","butter","ghee","buttermilk","khoya","mawa","dahi"]),
 ("Oils & Fats", ["oil","ghee","butter"]),
 ("Vegetables", ["onion","tomato","potato","carrot","cabbage","spinach","palak","peas","capsicum","bell pepper","brinjal","eggplant","okra","karela","bitter gourd","gourd","pumpkin","kaddu","beetroot","cauliflower","gobi","mushroom","radish","mooli","beans","corn","chilli","chili","garlic","lahsun","ginger","adrak","cucumber","drumstick","bhindi","shallot","lettuce","colocasia","tindora","methi leaves","curry leaves","spring onion","green pepper","yam","plantain","lauki","bottle gourd","ash gourd","white pumpkin","ridge gourd","snake gourd","taro"]),
 ("Fruits", ["mango","banana","apple","orange","lemon","lime","pineapple","grape","guava","papaya","pomegranate","watermelon","coconut","tamarind","imli","jackfruit","amla","dates","raisin","kishmish","jaggery fruit"]),
 ("Herbs", ["coriander leaves","cilantro","dhania leaves","mint","pudina","curry leaves","basil","parsley","dill","fenugreek leaves","kasuri methi","bay leaf","tej patta","rose petals","lemongrass"]),
 ("Spices & Seasonings", ["salt","pepper","turmeric","haldi","cumin","jeera","coriander powder","dhania powder","chilli powder","chili powder","garam masala","mustard seeds","rai","asafoetida","hing","fennel","saunf","cardamom","elaichi","cinnamon","dalchini","clove","laung","lavang","nutmeg","saffron","amchur","amchur powder","paprika","methi seeds","ajwain","star anise","kalonji","mace","stone flower","kala jeera","black pepper","red chilli","green chilli","red chili","green chili","curry powder","chutney powder","sambar powder","rasam powder","baking powder","baking soda","vanilla","hing powder","mustard powder","chana masala"]),
 ("Pulses & Legumes", ["dal","dhal","lentil","chickpea","chana","urad","udad","moong","mung","rajma","kidney bean","toor","arhar","masoor","lobia","black eyed pea","black-eyed pea","soy","soya","tofu","gram","besan","bengal gram","horse gram","kulith","chowli"]),
 ("Grains & Flours", ["rice","flour","atta","maida","sooji","suji","barley","jowar","ragi","wheat","semolina","rava","vermicelli","semiya","oats","muesli","sabudana","quinoa","millet","poha","flattened rice","rice flour","corn flour","cornmeal","bread crumbs","breadcrumbs","noodles","pasta","dosa batter","idli batter","ragi flour"]),
 ("Nuts & Seeds", ["almond","badam","cashew","kaju","peanut","groundnut","moongphali","pistachio","pista","walnut","sesame","til","flaxseed","chia seed","sunflower seed","pumpkin seed","poppy seed","khus khus","coconut flakes"]),
 ("Sweeteners", ["sugar","jaggery","gur","honey","syrup","maple syrup","powdered sugar","icing sugar"]),
 ("Liquids", ["water","stock","broth","vinegar","lemon juice","lime juice","rose water","coconut milk","tomato puree","soy sauce","sauce","juice","extract","wine"]),
 ("Bakery & Pasta", ["bread","pasta","macaroni","spaghetti","puff pastry","pizza base","bun","buns","yeast","baking chocolate","chocolate chips"]),
]
PACKET_TERMS = {"packet","packets","packaged ingredient","packed ingredient","ready mix packet"}
BAD_INGREDIENT_TERMS = {
 "unparsed ingredient fragment","long","as per taste","as per use","take","required",
 "as required","to taste","water as required","salt to taste",""
}
FAMOUS = [
 ("Masala Dosa", ["masala dosa","mysore masala dosa"]),
 ("Idli", ["idli recipe","soft idli","idli"]),
 ("Sambar", ["sambar recipe","tiffin sambar","sambar"]),
 ("Paneer Butter Masala", ["paneer butter masala"]),
 ("Palak Paneer", ["palak paneer"]),
 ("Chole", ["punjabi chole","chole masala","chole"]),
 ("Rajma Masala", ["rajma masala"]),
 ("Dal Tadka", ["dal tadka","yellow dal tadka","dal fry"]),
 ("Aloo Gobi", ["aloo gobi","aloo gobhi"]),
 ("Butter Chicken", ["butter chicken"]),
 ("Chicken Biryani", ["chicken biryani"]),
 ("Vegetable Biryani", ["vegetable biryani","veg biryani"]),
 ("Samosa", ["samosa recipe","punjabi samosa","samosa"]),
 ("Pav Bhaji", ["pav bhaji"]),
 ("Poha", ["kanda poha","poha recipe","poha"]),
 ("Upma", ["rava upma","vegetable upma","upma"]),
 ("Dhokla", ["khaman dhokla","dhokla"]),
 ("Rogan Josh", ["rogan josh"]),
 ("Fish Curry", ["fish curry"]),
 ("Prawn Masala", ["prawn masala","prawns masala"]),
 ("Appam", ["appam recipe","appam"]),
 ("Pesarattu", ["pesarattu"]),
 ("Lemon Rice", ["lemon rice"]),
 ("Tomato Rice", ["tomato rice"]),
 ("Gulab Jamun", ["gulab jamun"]),
 ("Rice Kheer", ["rice kheer","chawal ki kheer","kheer"]),
 ("Gajar Halwa", ["gajar halwa","carrot halwa"]),
 ("Raita", ["boondi raita","cucumber raita","raita"]),
 ("Aloo Paratha", ["aloo paratha"]),
 ("Dhokla", ["dhokla recipe","khaman dhokla"]),
]

def clean(v):
    return base.clean_text(str(v)) if v is not None else ""

def key(v):
    return base.norm_key(clean(v))

@lru_cache(maxsize=12000)
def category_for(name: str, aliases: tuple):
    # Use existing explainable classifier first; if still unknown, use a curated
    # culinary glossary mapping, considering parenthetical source aliases.
    cat, method, dim = base.classify_ingredient(name, aliases)
    if method != "unclassified" and cat != "Packaged & Prepared":
        return cat, method, dim
    candidates = [key(name)] + [key(a) for a in aliases]
    hits = []
    for category, terms in MANUAL_TYPE_RULES:
        for term in terms:
            t = key(term)
            if t and any(re.search(r"(^| )" + re.escape(t) + r"( |$)", candidate) for candidate in candidates):
                hits.append((len(t), category))
    if hits:
        cat = sorted(hits, reverse=True)[0][1]
        dim = "volume" if cat in {"Liquids", "Oils & Fats"} else "mass"
        return cat, "glossary_rule", dim
    return "Other / needs review", "unclassified", "unspecified"

def base_diet(raw):
    v=key(raw)
    if "non veget" in v or "nonveget" in v or "non vegetarian" in v:
        return "non_vegetarian"
    if "eggetarian" in v:
        return "eggetarian"
    if "veget" in v or "vegan" in v:
        return "vegetarian"
    return "unknown"

def valid_text(v):
    return bool(clean(v)) and not re.search(r"[\u0900-\u097F]", str(v))

def ingredient_name_ok(name):
    k=key(name)
    if not k or k in BAD_INGREDIENT_TERMS or len(clean(name)) > 48:
        return False
    if re.match(r"^\s*[–—-]?\s*\d", clean(name)):
        return False
    if re.fullmatch(r"[\d\s./+-]+", clean(name)):
        return False
    if re.search(r"\b(?:as per taste|as per use|as required|unparsed|quantity|ingredients?)\b", k):
        return False
    # Keep normal culinary punctuation but reject stray numeric/symbol-only debris.
    if re.fullmatch(r"[\W\d_]+", clean(name), flags=re.UNICODE):
        return False
    return True

def display_recipe_name(value):
    # Remove parenthetical/bracketed alternate names and redundant repeated titles.
    n=clean(value)
    n=re.sub(r"\s*\([^()]*\)", "", n)
    n=re.sub(r"\s*\[[^\[\]]*\]", "", n)
    n=clean(n)
    if " - " in n:
        left,right=n.split(" - ",1)
        if key(left)==key(right):
            n=clean(left)
    n=re.sub(r"\s+recipe\s*$", "", n, flags=re.I)
    return clean(n)

def recipe_name_ok(name):
    n=clean(name)
    return (bool(n) and len(n)<=55 and not re.search(r"[\u0900-\u097F]", n)
            and not re.search(r"\d", n)
            and not re.search(r"[<>@#$%^*_={}()[\]|\\]", n)
            and len(n.split())<=8)

def parse_source_ingredient(segment):
    # The source frequently writes mixed fractions as "1 1/2 cup". The shared
    # parser expects the equivalent hyphen form, so normalize only for parsing.
    fixed=re.sub(r"^\s*[–—-]\s*(?=\d)", "", str(segment))
    fixed=re.sub(r"^\s*(\d+)\s+(\d+\s*/\s*\d+)(?=\s)",lambda m:m.group(1)+"-"+re.sub(r"\s+","",m.group(2)),fixed)
    return base.parse_ingredient(fixed)

def main():
    raw=pd.read_csv(SOURCE,compression="zip",dtype=str,keep_default_na=False)
    # Normalize core fields and retain only translated/English records.
    candidates=[]
    rejects=[]
    seen_names=set()
    for ix,row in raw.iterrows():
        name=display_recipe_name(row.get("TranslatedRecipeName",""))
        ingr=clean(row.get("TranslatedIngredients",""))
        inst=clean(row.get("TranslatedInstructions",""))
        reasons=[]
        if not recipe_name_ok(name): reasons.append("recipe_name_long_or_malformed")
        if not valid_text(ingr) or not valid_text(inst): reasons.append("missing_or_non_english_translated_content")
        try:
            prep=int(float(row.get("PrepTimeInMins","") or 0))
            cook=int(float(row.get("CookTimeInMins","") or 0))
            total=int(float(row.get("TotalTimeInMins","") or 0))
            servings=int(float(row.get("Servings","") or 0))
        except Exception:
            prep=cook=total=servings=-1
        if total<1 or total>240 or prep<0 or cook<0 or servings<1 or servings>30:
            reasons.append("time_or_servings_out_of_demo_range")
        if not clean(row.get("Cuisine","")): reasons.append("missing_cuisine")
        if not clean(row.get("Course","")): reasons.append("missing_course")
        diet=base_diet(row.get("Diet",""))
        if diet=="unknown": reasons.append("unknown_diet")
        nk=key(name)
        if nk in seen_names: reasons.append("duplicate_translated_recipe_name")
        if reasons:
            rejects.append({"source_row":ix+2,"source_recipe_id":row.get("Srno",""),"recipe_name":name,"reject_reasons":";".join(sorted(set(reasons)))})
            continue
        seen_names.add(nk)
        parsed=[]
        parse_bad=[]
        for pos,seg in enumerate(base.split_outside_parentheses(ingr),1):
            p=parse_source_ingredient(seg)
            pname=clean(p.ingredient_name)
            aliases=[clean(a) for a in p.aliases if clean(a)]
            cat,method,dim=category_for(pname,tuple(aliases))
            if not ingredient_name_ok(pname):
                parse_bad.append(f"bad_ingredient_name:{pname}")
            if method=="unclassified" or cat=="Other / needs review":
                parse_bad.append(f"unclassified_ingredient:{pname}")
            # Preserve aliases, but do not silently merge alias collisions.
            parsed.append({"position":pos,"raw_text":clean(seg),"ingredient_name":pname,
                           "ingredient_key":key(pname),"aliases":aliases,"quantity_raw":clean(p.quantity_raw),
                           "unit":clean(p.unit),"prep_note":clean(p.prep_note),"is_optional":bool(p.is_optional),
                           "ingredient_type":cat,"classification_method":method,"default_unit_dimension":dim})
        if not parsed: parse_bad.append("no_ingredients")
        if parse_bad:
            rejects.append({"source_row":ix+2,"source_recipe_id":row.get("Srno",""),"recipe_name":name,
                            "reject_reasons":";".join(sorted(set(parse_bad)))})
            continue
        candidates.append({"source_row":ix+2,"source_recipe_id":row.get("Srno",""),"source":row.to_dict(),
                           "recipe_name":name,"recipe_key":nk,"prep":prep,"cook":cook,"total":total,
                           "servings":servings,"diet":diet,"ingredients":parsed})
    # If too few records meet the strict all-ingredients-classified gate, stop rather
    # than silently weakening the promised quality threshold.
    if len(candidates)<1000:
        pd.DataFrame(rejects).to_csv(AUDIT/"selection_rejections.csv",index=False)
        report={"source_rows":len(raw),"strict_eligible_recipes":len(candidates),
                "target_recipes":1000,"status":"BLOCKED_BY_STRICT_QUALITY_GATE",
                "reason":"Fewer than 1000 recipes passed the explicit quality gate; criteria were not silently relaxed."}
        (AUDIT/"quality_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        raise RuntimeError(f"Only {len(candidates)} strict-clean recipes passed. See {AUDIT/'quality_report.json'}")
    # Build a diversity-aware 1000: first cover cuisine/course/diet strata, then
    # fill by score while limiting overrepresentation from a single cuisine.
    def quality_score(r):
        s=r["source"]
        n=key(r["recipe_name"])
        popular_terms=[key(x[0]) for x in FAMOUS]
        simple_dish=any(n == term or n.startswith(term+" recipe") or n.startswith(term+" ") for term in popular_terms if term)
        fusion_penalty=any(term in n for term in ["pizza","pasta","soup","muesli","pinwheel","galette","momo","salad","pudding","trifle","barfi","peanut butter chicken"])
        return (int(bool(clean(s.get("URL",""))))*3 + int(bool(clean(s.get("TranslatedInstructions",""))))*3
                + int(len(r["recipe_name"])<=38)*3 + int(r["total"]<=90)*2
                + int(4<=len(r["ingredients"])<=18)*2
                + int(bool(clean(s.get("Cuisine","")))) + int(bool(clean(s.get("Course",""))))
                + int(simple_dish)*12 - int(fusion_penalty)*10)
    for r in candidates:
        r["score"]=quality_score(r)
        r["cuisine"]=clean(r["source"].get("Cuisine",""))
        r["course"]=clean(r["source"].get("Course",""))
    candidates.sort(key=lambda r:(-r["score"],r["recipe_key"]))
    selected=[]
    selected_keys=set()
    cuisine_counts=Counter()
    # Round-robin cuisine and diet to increase breadth before filling remaining slots.
    by_cuisine=defaultdict(list)
    for r in candidates: by_cuisine[r["cuisine"]].append(r)
    cuisines=sorted(by_cuisine, key=lambda c:(-len(by_cuisine[c]),c))
    cursor=0
    while len(selected)<1000:
        added=False
        for cuisine in cuisines:
            rows=by_cuisine[cuisine]
            while cursor < len(rows) and rows[cursor]["recipe_key"] in selected_keys: cursor+=1
            # reset per-cuisine cursor is implemented below by position map
        break
    pos={c:0 for c in cuisines}
    while len(selected)<1000:
        progress=False
        for cuisine in cuisines:
            rows=by_cuisine[cuisine]
            while pos[cuisine]<len(rows) and rows[pos[cuisine]]["recipe_key"] in selected_keys:
                pos[cuisine]+=1
            if pos[cuisine]>=len(rows): continue
            # Soft cap encourages breadth; relax only if needed to reach target.
            if cuisine_counts[cuisine]>=80 and any(cuisine_counts[c]<80 and pos[c]<len(by_cuisine[c]) for c in cuisines):
                continue
            r=rows[pos[cuisine]]; pos[cuisine]+=1
            selected.append(r); selected_keys.add(r["recipe_key"]); cuisine_counts[cuisine]+=1; progress=True
            if len(selected)>=1000: break
        if not progress:
            for r in candidates:
                if r["recipe_key"] not in selected_keys:
                    selected.append(r); selected_keys.add(r["recipe_key"])
                    if len(selected)>=1000: break
    selected=selected[:1000]
    # Canonical ingredient IDs based on normalized primary translated ingredient name.
    ing_groups=defaultdict(list)
    for r in selected:
        for ing in r["ingredients"]:
            ing_groups[ing["ingredient_key"]].append((r,ing))
    ingredient_ids={k:i for i,k in enumerate(sorted(ing_groups),1)}
    ingredient_rows=[]; alias_rows=[]; recipe_rows=[]; relation_rows=[]; tuple_rows=[]; reverse_rows=[]
    alias_map=defaultdict(set)
    for k,items in ing_groups.items():
        for r,ing in items:
            alias_map[key(ing["ingredient_name"])].add(k)
            for a in ing["aliases"]:
                if key(a): alias_map[key(a)].add(k)
    for k in sorted(ing_groups):
        items=ing_groups[k]; names=Counter(ing["ingredient_name"] for _,ing in items)
        canonical=names.most_common(1)[0][0]; ing_id=ingredient_ids[k]
        type_counts=Counter(ing["ingredient_type"] for _,ing in items)
        itype=type_counts.most_common(1)[0][0]
        dims=Counter(ing["default_unit_dimension"] for _,ing in items)
        dim=dims.most_common(1)[0][0]
        if itype=="Liquids": suggested="ml, l, cup, tbsp, tsp"
        elif itype=="Oils & Fats": suggested="ml, tbsp, tsp"
        elif itype in {"Vegetables","Fruits","Dairy & Eggs","Meat & Seafood"}: suggested="g, kg, piece"
        elif itype in {"Herbs","Spices & Seasonings","Sweeteners"}: suggested="g, tsp, tbsp"
        elif itype in {"Pulses & Legumes","Grains & Flours","Nuts & Seeds","Bakery & Pasta"}: suggested="g, kg, cup"
        else: suggested="g, ml, piece"
        observed=sorted({ing["unit"] for _,ing in items if ing["unit"]})
        ingredient_rows.append({"ingredient_id":ing_id,"canonical_name":canonical,"canonical_key":k,
                                "ingredient_type":itype,"classification_method":Counter(ing["classification_method"] for _,ing in items).most_common(1)[0][0],
                                "default_unit_dimension":dim,"suggested_units":suggested,
                                "observed_units":" | ".join(observed),"recipe_occurrences":len(items),
                                "recipe_count":len({r["recipe_key"] for r,_ in items})})
        aliases={canonical}
        for _,ing in items:
            aliases.add(ing["ingredient_name"])
            aliases.update(ing["aliases"])
        for a in sorted(aliases,key=str.casefold):
            if key(a):
                alias_rows.append({"ingredient_id":ing_id,"canonical_name":canonical,"alias":a,
                                   "alias_key":key(a),"alias_source":"primary_name_or_parenthetical_source_alias"})
    # Stable IDs are assigned from the source name sort, then selected order is preserved.
    for rid,r in enumerate(selected,1):
        s=r["source"]
        diet=r["diet"]
        rawdiet=clean(s.get("Diet",""))
        specific=rawdiet if key(rawdiet) not in {"vegetarian","non vegeterian","non vegetarian","non vegetarian","eggetarian","vegan"} else ""
        recipe_rows.append({"recipe_id":rid,"source_recipe_id":r["source_recipe_id"],"recipe_name":r["recipe_name"],
            "prep_time_min":r["prep"],"cook_time_min":r["cook"],"total_time_min":r["total"],"servings":r["servings"],
            "cuisine":r["cuisine"],"course":r["course"],"diet":diet,"specific_diet":specific,
            "instructions":clean(s.get("TranslatedInstructions","")),"url":clean(s.get("URL",""))})
        for ing in r["ingredients"]:
            iid=ingredient_ids[ing["ingredient_key"]]
            relation_rows.append({"recipe_id":rid,"ingredient_position":ing["position"],"ingredient_id":iid,
                "ingredient_name":ing["ingredient_name"],"quantity_raw":ing["quantity_raw"],"unit":ing["unit"],
                "unit_dimension":base.UNIT_DIMENSIONS.get(ing["unit"],"unspecified"),
                "prep_note":ing["prep_note"],"is_optional":ing["is_optional"],"raw_text":ing["raw_text"]})
            tuple_rows.append({"recipe_id":rid,"ingredient_id":iid,"quantity_raw":ing["quantity_raw"],"unit":ing["unit"]})
            reverse_rows.append({"ingredient_id":iid,"canonical_name":ingredient_rows[iid-1]["canonical_name"],
                "recipe_id":rid,"recipe_name":r["recipe_name"]})
    recipes_df=pd.DataFrame(recipe_rows)
    ingredients_df=pd.DataFrame(ingredient_rows)
    aliases_df=pd.DataFrame(alias_rows).drop_duplicates(["ingredient_id","alias_key"])
    rel_df=pd.DataFrame(relation_rows)
    tuple_df=pd.DataFrame(tuple_rows)
    reverse_df=pd.DataFrame(reverse_rows).drop_duplicates()
    recipes_df.to_csv(EXPORTS/"recipes_1000.csv",index=False,quoting=csv.QUOTE_MINIMAL)
    ingredients_df.to_csv(EXPORTS/"ingredients.csv",index=False)
    aliases_df.to_csv(EXPORTS/"ingredient_aliases.csv",index=False)
    rel_df.to_csv(EXPORTS/"recipe_ingredients.csv",index=False)
    tuple_df.to_csv(EXPORTS/"recipe_ingredient_tuples.csv",index=False)
    reverse_df.to_csv(EXPORTS/"ingredient_recipes.csv",index=False)
    # Type -> units table includes suggested units and actual source-observed units.
    type_rows=[]
    for typ,grp in ingredients_df.groupby("ingredient_type"):
        obs=sorted({u for joined in grp["observed_units"].astype(str) for u in joined.split(" | ") if u})
        dims=sorted(set(grp["default_unit_dimension"].astype(str)))
        type_rows.append({"ingredient_type":typ,"ingredient_count":int(len(grp)),
            "default_unit_dimensions":" | ".join(dims),"suggested_units":"; ".join(sorted(set(grp["suggested_units"]))),
            "observed_units_in_source":" | ".join(obs)})
    pd.DataFrame(type_rows).to_csv(EXPORTS/"ingredient_type_units.csv",index=False)
    # Alias collisions are evidence, not auto-merged identities.
    collision=aliases_df.groupby("alias_key").agg(candidate_count=("ingredient_id","nunique"),alias=("alias","first")).reset_index()
    collision=collision[collision["candidate_count"]>1]
    collision.to_csv(AUDIT/"alias_collisions.csv",index=False)
    # Select famous demo recipes only from the strict clean set; match exact-ish normalized names.
    norm_to_r={r["recipe_key"]:(i+1,r) for i,r in enumerate(selected)}
    demo=[]
    for display,patterns in FAMOUS:
        found=None
        for p in patterns:
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
                found=exact[0]; break
        if found and found[0] not in {d["recipe_id"] for d in demo}:
            demo.append({"recipe_id":found[0],"demo_display_name":display,"match_name":found[1]["recipe_name"],
                         "reason":"Familiar dish; passed the same strict ingredient and metadata quality gate."})
    # If curated names are missing, fill with diverse short clean dishes to exactly 30.
    if len(demo)<30:
        used={d["recipe_id"] for d in demo}
        for rid,r in enumerate(selected,1):
            if rid in used: continue
            demo.append({"recipe_id":rid,"demo_display_name":r["recipe_name"],"match_name":r["recipe_name"],
                         "reason":"Quality-passed fallback chosen to broaden cuisine/course/diet coverage."})
            used.add(rid)
            if len(demo)>=30: break
    demo=demo[:30]
    demo_ids={d["recipe_id"] for d in demo}
    pd.DataFrame(demo).to_csv(EXPORTS/"demo_30_selection.csv",index=False)
    recipes_df[recipes_df.recipe_id.isin(demo_ids)].to_csv(EXPORTS/"demo_30_recipes.csv",index=False)
    rel_df[rel_df.recipe_id.isin(demo_ids)].to_csv(EXPORTS/"demo_30_recipe_ingredients.csv",index=False)
    # Explain exclusions and selected recipe coverage.
    pd.DataFrame(rejects).to_csv(AUDIT/"selection_rejections.csv",index=False)
    cuisine_counts=recipes_df["cuisine"].value_counts().to_dict()
    course_counts=recipes_df["course"].value_counts().to_dict()
    diet_counts=recipes_df["diet"].value_counts().to_dict()
    report={"source_rows":int(len(raw)),"strict_eligible_recipes_before_selection":int(len(candidates)),
        "selected_unique_recipes":int(len(recipes_df)),"demo_recipes":int(len(demo)),
        "selected_ingredient_rows":int(len(rel_df)),"unique_ingredients":int(len(ingredients_df)),
        "alias_rows":int(len(aliases_df)),"alias_collision_keys":int(len(collision)),
        "unclassified_selected_ingredients":int((ingredients_df.ingredient_type=="Other / needs review").sum()),
        "cuisines":cuisine_counts,"courses":course_counts,"diet_labels":diet_counts,
        "quality_rules":{"recipe_name_max_chars":55,"ingredient_name_max_chars":48,"total_time_minutes": "1..240",
            "servings":"1..30","all_ingredients_must_be_classified":True,"no_numeric_recipe_names":True,
            "translated_fields_only":True,"duplicate_recipe_names_excluded":True,"unknown_diet_excluded":True},
        "web_references":[
          {"title":"Indian Ingredients Glossary - WebIndia123","url":"https://www.webindia123.com/cookery/measures/IndianIngredientsGlossary.html","use":"Cross-check common English/Hindi ingredient names and food types."},
          {"title":"Indian Spices Glossary - Veg Recipes of India","url":"https://www.vegrecipesofindia.com/indian-spices-glossary-of-indian-spices-in-english-and-hindi/","use":"Cross-check common spice transliterations and aliases."},
          {"title":"IndianFoodDatasetGeneration source documentation","url":"https://github.com/kanishk307/IndianFoodDatasetGeneration","use":"Confirm source dataset fields and translation provenance."}
        ],
        "limitations":["Classification uses source parenthetical aliases, transparent keyword rules, and broad web glossaries; it is not an individual web search for every ingredient.",
          "Suggested units are type-level guidance, not conversion factors. Quantities remain source text.",
          "Aliases are preserved as evidence; collisions are reported and not automatically merged.",
          "The demo subset is selected from the strict-clean 1,000; if a famous dish is absent from that clean pool, a quality-passed diverse fallback fills the 30 slots."]}
    (AUDIT/"quality_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["source_rows","strict_eligible_recipes_before_selection","selected_unique_recipes","demo_recipes","selected_ingredient_rows","unique_ingredients","alias_rows","alias_collision_keys","unclassified_selected_ingredients"]},indent=2))
    print("DEMO",json.dumps(demo,ensure_ascii=False))
    print("TOP_CUISINES",json.dumps(recipes_df["cuisine"].value_counts().head(20).to_dict(),ensure_ascii=False))
    print("OUTPUT",str(OUT))

if __name__=="__main__":
    main()
