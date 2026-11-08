@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set DEV_WORKER=e
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\run_dev.py F-rel >> logs\run_dev_e.log 2>&1
