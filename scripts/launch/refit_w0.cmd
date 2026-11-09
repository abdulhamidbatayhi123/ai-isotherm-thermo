@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set WORLD_WORKER=r0
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\verdict_worlds.py run KS0 DA FW FLAT SUB --shard 0/4 >> logs\worlds_r0.log 2>&1
