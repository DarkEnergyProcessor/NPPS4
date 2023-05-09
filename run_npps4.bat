setlocal enabledelayedexpansion

if "%VIRTUAL_ENV%"=="" (
	IF NOT EXIST "venv" (
		echo Cannot find virtual environment. Is it installed?
		exit /b 1
	)
	set UVICORN=venv\Scripts\uvicorn
) else (
	set UVICORN=%VIRTUAL_ENV%\Scripts\uvicorn
)

"%UVICORN%" npps4:uvicorn_main --port 51376 %*
