@echo off
REM Запуск тестов с TensorFlow из venv на диске D

set PYTHONPATH=D:\tf_env\Lib\site-packages;%PYTHONPATH%
cd "d:\Нова папка\air-raid-alerts-analysis"

echo Запуск pytest с PYTHONPATH из D:\tf_env...
D:\tf_env\Scripts\pytest.exe tests/ -v

echo.
echo Тесты завершены!
pause
