@echo off
echo 🔧 Switching to D: drive Python...

:: Add D: drive Python to PATH
set PATH=D:\miniconda3;D:\miniconda3\Scripts;%PATH%

echo ✅ Now using D: drive Python
echo.
python --version
echo.
echo To test: python -c "import space_app; print('Space app works!')"
echo.