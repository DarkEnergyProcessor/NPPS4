#!/bin/bash

cd /NPPS4/

if [ ! -d "venv" ]; then
	python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
pip install asyncpg

if [ ! -f "/data/config.toml" ]; then
        cp config.sample.toml /data/config.toml
	sed -i 's|data/main.sqlite3|/data/main.sqlite3|g' /data/config.toml
	echo "Setup complete. Please edit data/config.toml and re-run the container"
	exit 1
fi

if [ ! -f "/data/server_data.json" ]; then
        cp npps4/server_data.json /data/server_data.json
        sed -i 's|server_data = "npps4/server_data.json"|server_data = "/data/server_data.json"|g' /data/config.toml
        cp npps4/server_data_schema.json /data/server_data_schema.json
fi

port="${PORT:-51376}"

export NPPS4_CONFIG=/data/config.toml

alembic upgrade head
echo "Starting..."
uvicorn npps4.run.app:main --port $port --host 0.0.0.0 --reload
