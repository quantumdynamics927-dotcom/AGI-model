@echo off
REM Deploy Scientific Python Ecosystem to Hugging Face Spaces
REM 
REM Prerequisites:
REM 1. pip install huggingface_hub
REM 2. huggingface-cli login
REM 3. Set HF_TOKEN environment variable (optional)
REM
REM Usage:
REM   deploy_windows.bat
REM   deploy_windows.bat --space-name "my-custom-name"
REM   deploy_windows.bat --private

echo ============================================
echo Scientific Python Ecosystem HF Space Deploy
echo ============================================
echo.

REM Check if huggingface_hub is installed
python -c "import huggingface_hub" 2>nul
if errorlevel 1 (
    echo Installing huggingface_hub...
    pip install huggingface_hub
)

REM Run deployment
python deploy_to_hf_space.py %*

echo.
echo ============================================
echo Deployment complete!
echo ============================================
pause