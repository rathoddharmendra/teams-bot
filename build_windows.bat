@echo off
setlocal

python -c "from icon import generate_icon; generate_icon(True).save('icon.ico', format='ICO', sizes=[(64,64)])"

pyinstaller ^
  --onefile ^
  --windowed ^
  --name TeamsKeepAlive ^
  --icon icon.ico ^
  main.py

echo Built: dist\TeamsKeepAlive.exe
