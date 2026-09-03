@echo off
cd /d "d:\Estudios Actuales\Licenciatura en Tec. de Biocombustibles y E. Renovables\Proyecto SimBIO"

:: Inicia app_v1 en el puerto por defecto (8501)
start "SimBIO v1" streamlit run app_v1.py --server.port 8501

:: Inicia app_v2 en un puerto diferente (8502)
start "SimBIO v2" streamlit run app_v2.py --server.port 8502

:: Inicia app_v3 en un puerto diferente (8502)
start "SimBIO v3" streamlit run app_v3.py --server.port 8503

pause