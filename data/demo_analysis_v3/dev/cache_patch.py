from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
if "from functools import lru_cache" not in s:
 s=s.replace("from collections import Counter, defaultdict","from collections import Counter, defaultdict\nfrom functools import lru_cache")
s=s.replace("def category_for(name, aliases):","@lru_cache(maxsize=12000)\ndef category_for(name: str, aliases: tuple):")
s=s.replace("cat,method,dim=category_for(pname,aliases)","cat,method,dim=category_for(pname,tuple(aliases))")
p.write_text(s,encoding="utf-8")
print("cache patched")
