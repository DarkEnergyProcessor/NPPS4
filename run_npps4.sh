if [ -z "$VIRTUAL_ENV" ]; then
	if [ ! -d "venv" ]; then
		echo "Cannot find virtual environment. Is it installed?"
		exit 1
	fi
	UVICORN="venv/bin/uvicorn"
else
	UVICORN="$VIRTUAL_ENV/bin/uvicorn"
fi

"$UVICORN" npps4.run.app:main --port 51376 "$@"
