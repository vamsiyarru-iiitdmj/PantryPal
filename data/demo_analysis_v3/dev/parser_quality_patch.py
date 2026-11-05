from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
s=s.replace('''    if method != "unclassified":
        return cat, method, dim''','''    if method != "unclassified" and cat != "Packaged & Prepared":
        return cat, method, dim''')
s=s.replace('''    if not k or k in BAD_INGREDIENT_TERMS or len(clean(name)) > 48:
        return False''','''    if not k or k in BAD_INGREDIENT_TERMS or len(clean(name)) > 48:
        return False
    if re.match(r"^\\\\s*\\\\d", clean(name)):
        return False''')
s=s.replace('''def main():
    raw=pd.read_csv(SOURCE,compression="zip",dtype=str,keep_default_na=False)''','''def parse_source_ingredient(segment):
    # The source frequently writes mixed fractions as "1 1/2 cup". The shared
    # parser expects the equivalent hyphen form, so normalize only for parsing.
    fixed=re.sub(r"^\\\\s*(\\\\d+)\\\\s+(\\\\d+\\\\s*/\\\\s*\\\\d+)(?=\\\\s)",lambda m:m.group(1)+"-"+re.sub(r"\\\\s+","",m.group(2)),str(segment))
    return base.parse_ingredient(fixed)

def main():
    raw=pd.read_csv(SOURCE,compression="zip",dtype=str,keep_default_na=False)''')
s=s.replace('''            p=base.parse_ingredient(seg)
            pname=clean(p.ingredient_name)''','''            p=parse_source_ingredient(seg)
            pname=clean(p.ingredient_name)''')
s=s.replace('''"position":pos,"raw_text":clean(p.raw_text),"ingredient_name":pname,''','''"position":pos,"raw_text":clean(seg),"ingredient_name":pname,''')
p.write_text(s,encoding="utf-8")
print("mixed-fraction and category patch applied")
