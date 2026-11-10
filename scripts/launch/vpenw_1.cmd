@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
start "" /belownormal /b /wait "C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\explore_vpen_weight.py --shard 1/2 >> logs\explore_vpen_weight_1.log 2>&1
