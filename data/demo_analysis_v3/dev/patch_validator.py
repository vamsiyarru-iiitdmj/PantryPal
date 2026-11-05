from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\final_validation.py")
s=p.read_text(encoding="utf-8")
s=s.replace('"ingredient_names_starting_with_digit":int(i.canonical_name.str.match(r"^\\s*\\d",na=False).sum()),',
'"ingredient_names_with_quantity_prefix":int(i.canonical_name.str.match(r"^\\s*[–—-]?\\s*\\d",na=False).sum()),')
s=s.replace('checks["ingredient_names_starting_with_digit"]==0','checks["ingredient_names_with_quantity_prefix"]==0')
p.write_text(s,encoding="utf-8")
print("validator quantity-prefix rule updated")
