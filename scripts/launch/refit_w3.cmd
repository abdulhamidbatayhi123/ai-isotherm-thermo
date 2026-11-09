@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
set OMP_NUM_THREADS=1
set WORLD_WORKER=r3
"C:\Users\abdulhamid batayhi\Desktop\ai-mof-cof-dynamics\.venv\Scripts\python.exe" scripts\verdict_worlds.py run KS0 DA FW FLAT SUB --shard 3/4 >> logs\worlds_r3.log 2>&1
