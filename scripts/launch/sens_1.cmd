@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity rule5_v1 --shard 1/2 >> logs\sens_rule5_v1_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity rule5_v2 --shard 1/2 >> logs\sens_rule5_v2_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity rule5_none --shard 1/2 >> logs\sens_rule5_none_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity minpoints7 --shard 1/2 >> logs\sens_minpoints7_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity co2cl2_s8 --shard 1/2 >> logs\sens_co2cl2_s8_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity perturb_s1 --shard 1/2 >> logs\sens_perturb_s1_1.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_confirmatory.py --sensitivity perturb_s2 --shard 1/2 >> logs\sens_perturb_s2_1.log 2>&1
