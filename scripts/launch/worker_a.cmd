@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set DEV_WORKER=a
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_dev.py P V-none V-pen P-K >> logs\run_dev_a.log 2>&1
