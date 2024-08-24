#!/bin/bash

cd /NPPS4/

if [ ! -d "venv" ]; then
	python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

if [ ! -f "/data/config.toml" ]; then
        cp config.sample.toml /data/config.toml
	sed -i 's|data/main.sqlite3|/data/main.sqlite3|g' /data/config.toml
	echo "Setup complete. Please edit data/config.toml and re-run the container"
	exit 1
fi

port="${PORT:-51376}"

export NPPS4_CONFIG=/data/config.toml

alembic upgrade head
echo "Starting..."
uvicorn npps4.run.app:main --port $port --host 0.0.0.0 --reload
