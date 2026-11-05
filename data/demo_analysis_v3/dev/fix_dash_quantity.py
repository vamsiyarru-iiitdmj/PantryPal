from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
s=s.replace('''    if re.match(r"^\\s*\\d", clean(name)):
        return False''','''    if re.match(r"^\\s*[–—-]?\\s*\\d", clean(name)):
        return False''')
s=s.replace('''    fixed=re.sub(r"^\\s*(\\d+)\\s+(\\d+\\s*/\\s*\\d+)(?=\\s)",lambda m:m.group(1)+"-"+re.sub(r"\\s+","",m.group(2)),str(segment))
    return base.parse_ingredient(fixed)''','''    fixed=re.sub(r"^\\s*[–—-]\\s*(?=\\d)", "", str(segment))
    fixed=re.sub(r"^\\s*(\\d+)\\s+(\\d+\\s*/\\s*\\d+)(?=\\s)",lambda m:m.group(1)+"-"+re.sub(r"\\s+","",m.group(2)),fixed)
    return base.parse_ingredient(fixed)''')
p.write_text(s,encoding="utf-8")
print("dash-prefixed quantities handled")
