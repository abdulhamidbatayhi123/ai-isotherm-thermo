@echo off
cd /d "C:\Usersbdulhamid batayhi\Desktopi-isotherm-thermo"
set OMP_NUM_THREADS=1
start "" /belownormal /b /wait "C:\Usersbdulhamid batayhi\Desktopi-mof-cof-dynamics\.venv\Scripts\python.exe" scriptsxplore_vpen_weight.py --shard 1/2 >> logsxplore_vpen_weight_1.log 2>&1
