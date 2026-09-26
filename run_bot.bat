@echo off
cd /d C:\Users\stepc\job-hunter
:loop
"C:\Users\stepc\AppData\Local\Python\pythoncore-3.14-64\python.exe" -u main.py >> bot.log 2>&1
echo [%date% %time%] main.py exited, restart in 30s >> bot.log
timeout /t 30 /nobreak >nul
goto loop
