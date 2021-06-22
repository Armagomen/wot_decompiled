@echo off
   for /f "delims=" %%i in ('dir /a-d/b/s *.pyc_dis') do ren "%%i" "%%~ni.py"
exit /b