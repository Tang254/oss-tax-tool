@echo off
setlocal

python -m PyInstaller --noconfirm --onefile --windowed --name OSS-Tax-Tool oss_tax_tool_gui.py

echo.
echo Build finished. If successful, the EXE will be in the dist folder.
pause
