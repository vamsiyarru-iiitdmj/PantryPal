from pathlib import Path
p=Path(r"C:\Users\repal\OneDrive\Desktop\PantryPal\PantryPal\data\demo_analysis_v3\build_demo_dataset.py")
s=p.read_text(encoding="utf-8")
s=s.replace(r'r"^\\s*\\d"', r'r"^\s*\d"')
s=s.replace(r'r"^\\s*(\\d+)\\s+(\\d+\\s*/\\s*\\d+)(?=\\s)"', r'r"^\s*(\d+)\s+(\d+\s*/\s*\d+)(?=\s)"')
s=s.replace(r'r"\\s+"', r'r"\s+"')
p.write_text(s,encoding="utf-8")
print("fixed regex literals")
