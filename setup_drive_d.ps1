# PowerShell script to configure D: drive Python as default
# Run this script to set up your environment

Write-Host "Setting up D: drive Python environment..." -ForegroundColor Green

# Check if D: drive Miniconda exists
if (Test-Path "D:\miniconda3\python.exe") {
    Write-Host "Found Miniconda on D: drive" -ForegroundColor Green
    
    # Add D: drive Python to PATH temporarily for this session
    $env:PATH = "D:\miniconda3;D:\miniconda3\Scripts;" + $env:PATH
    
    Write-Host "Updated PATH to include D: drive Python" -ForegroundColor Green
    
    # Test the installation
    Write-Host "Testing Python installation..." -ForegroundColor Yellow
    $pythonVersion = & "D:\miniconda3\python.exe" --version
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
    
    # Test Gradio import
    Write-Host "Testing Gradio import..." -ForegroundColor Yellow
    & "D:\miniconda3\python.exe" -c "import gradio; print('Gradio imports successfully!')"
    
    # Test space_app import (may fail due to dependencies, but test basic functionality)
    Write-Host "Testing space_app basic functionality..." -ForegroundColor Yellow
    & "D:\miniconda3\python.exe" -c "import sys; sys.path.insert(0, '.'); 
try:
    import space_app
    print('Space app imports successfully!')
except ImportError as e:
    print('Space app import failed (expected due to dependencies):')
    print(str(e))
    print('But basic Python environment is working!')
"
    
    Write-Host ""
    Write-Host "D: drive Python setup complete!" -ForegroundColor Green
    Write-Host "To use D: drive Python permanently, add these to your PATH:" -ForegroundColor Cyan
    Write-Host "  D:\miniconda3" -ForegroundColor White
    Write-Host "  D:\miniconda3\Scripts" -ForegroundColor White
    
} else {
    Write-Host "Miniconda not found on D: drive" -ForegroundColor Red
    Write-Host "Please install Miniconda to D:\miniconda3" -ForegroundColor Yellow
}