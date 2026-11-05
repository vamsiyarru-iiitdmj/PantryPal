from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
needle='''def recipe_name_ok(name):
    n=clean(name)
    return (bool(n) and len(n)<=55 and not re.search(r"[\\u0900-\\u097F]", n)
            and not re.search(r"\\d", n)
            and not re.search(r"[<>@#$%^*_={}[\]|\\\\]", n)
            and len(n.split())<=8)
'''
replacement='''def display_recipe_name(value):
    # Remove parenthetical/bracketed alternate names and redundant repeated titles.
    n=clean(value)
    n=re.sub(r"\\s*\\([^()]*\\)", "", n)
    n=re.sub(r"\\s*\\[[^\\[\\]]*\\]", "", n)
    n=clean(n)
    if " - " in n:
        left,right=n.split(" - ",1)
        if key(left)==key(right):
            n=clean(left)
    n=re.sub(r"\\s+recipe\\s*$", "", n, flags=re.I)
    return clean(n)

def recipe_name_ok(name):
    n=clean(name)
    return (bool(n) and len(n)<=55 and not re.search(r"[\\u0900-\\u097F]", n)
            and not re.search(r"\\d", n)
            and not re.search(r"[<>@#$%^*_={}()[\\]|\\\\]", n)
            and len(n.split())<=8)
'''
if needle not in s: raise SystemExit("recipe_name_ok block not found")
s=s.replace(needle,replacement)
s=s.replace('name=clean(row.get("TranslatedRecipeName",""))','name=display_recipe_name(row.get("TranslatedRecipeName",""))')
p.write_text(s,encoding="utf-8")
print("recipe-name cleanup patched")
