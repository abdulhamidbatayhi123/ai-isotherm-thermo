@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set DEV_WORKER=b
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_dev.py A-pen >> logs\run_dev_b.log 2>&1
