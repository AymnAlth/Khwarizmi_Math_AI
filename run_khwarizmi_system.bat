@echo off
chcp 65001 >nul
echo =====================================================================
echo    نظام خوارزمي للذكاء الاصطناعي الرياضي الرمزي (Al-Khwarizmi Math AI)
echo =====================================================================
echo [*] جاري تشغيل خادم الذكاء الاصطناعي في WSL (CUDA GPU)...
start /b wsl -d Ubuntu-ML /home/ayman/miniforge3/envs/torch-gpu/bin/python /home/ayman/ml-workspace/projects/Khwarizmi_Math_AI/scripts/run_api.py

timeout /t 2 /nobreak >nul

echo [*] جاري تشغيل جسر الشبكة المحلية Wi-Fi Bridge للربط بالهاتف...
python d:/AI/DL/Khwarizmi_Math_AI/scripts/wifi_lan_bridge.py
