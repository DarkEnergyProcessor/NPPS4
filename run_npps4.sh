if [ -z "$VIRTUAL_ENV" ]; then
	if [ ! -d "venv" ]; then
		echo "Cannot find virtual environment. Is it installed?"
		exit 1
	fi
	PYTHON="venv/bin/python"
else
	PYTHON="$VIRTUAL_ENV/bin/python"
fi

"$PYTHON" main.py "$@"
