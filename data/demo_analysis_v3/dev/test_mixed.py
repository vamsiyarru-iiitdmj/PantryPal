import sys,re
sys.path.insert(0,r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal")
import build_recipe_data as b
for x in ["1-1/2 cup Basmati rice","1-1 / 2 cup Basmati rice","1-1/2 cups Basmati rice"]:
 p=b.parse_ingredient(x); print(x,repr(p.quantity_raw),repr(p.unit),repr(p.ingredient_name))
