@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set DEV_WORKER=d
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_dev.py F-hard C1 >> logs\run_dev_d.log 2>&1
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\mde.py 13 > logs\mde.log 2>&1
