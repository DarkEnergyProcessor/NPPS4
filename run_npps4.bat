setlocal enabledelayedexpansion

if "%VIRTUAL_ENV%"=="" (
	IF NOT EXIST "venv" (
		echo Cannot find virtual environment. Is it installed?
		exit /b 1
	)
	set PYTHON=venv\Scripts\python
) else (
	set PYTHON=%VIRTUAL_ENV%\Scripts\python
)

"%PYTHON%" main.py %*
endlocal
