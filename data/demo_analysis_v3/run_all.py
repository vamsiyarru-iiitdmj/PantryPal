from pathlib import Path
import subprocess,sys
base=Path(__file__).resolve().parent
steps=["build_demo_dataset.py","enrich_ingredient_forms.py","curate_demo30.py","finalize_report.py","final_validation.py"]
for step in steps:
 print("\n=== Running "+step+" ===",flush=True)
 result=subprocess.run([sys.executable,str(base/step)],cwd=str(base),check=False)
 if result.returncode:
  raise SystemExit(f"{step} failed with exit code {result.returncode}")
print("\nAll steps completed successfully.",flush=True)
