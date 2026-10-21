@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\streamlit.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto error
  .venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 goto error
)

.venv\Scripts\python.exe -m pip install -r requirements-lock-win.txt
if errorlevel 1 goto error
set JALA_MODE=local
.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1
exit /b %errorlevel%

:error
echo Gagal menyiapkan demo. Pastikan Python 3.12 tersedia dan koneksi paket aktif.
exit /b 1
