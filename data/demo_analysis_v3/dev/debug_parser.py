import sys
sys.path.insert(0,r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal")
import build_recipe_data as b
for x in ["1/2 cup Basmati rice","1/2 cups Basmati rice","1/2 liter Milk","1/2 tablespoon Corn flour","1 cup rice","1 teaspoon cumin seeds","2-1/2 cups rice","3 tablespoon Gram flour (besan)","6 Karela (Bitter Gourd/ Pavakkai) - deseeded"]:
 p=b.parse_ingredient(x)
 print(repr(x),"=>",repr(p.quantity_raw),repr(p.unit),repr(p.ingredient_name),repr(p.aliases),repr(p.prep_note))
