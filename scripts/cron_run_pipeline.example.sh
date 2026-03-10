#!/bin/zsh

PROJECT_DIR="/Users/olamideabioro/Documents/data analytics project/city_mobility_ops"

cd "$PROJECT_DIR" || exit 1

source "$PROJECT_DIR/.venv/bin/activate"

export DATABASE_URL="postgresql://postgres:xxxxxx@localhost:5432/mobility"
export GBFS_ROOT_URL="https://api.cyclocity.fr/contracts/dublin/gbfs/gbfs.json"
export GBFS_LANGUAGE="fr"

export OWM_API_KEY="xxxxxxxxxxxxxxxxxx"
export WEATHER_BASE_URL="https://api.openweathermap.org/data/2.5/forecast"
export WEATHER_CITY="Dublin"
export WEATHER_COUNTRY="IE"

python "$PROJECT_DIR/scripts/run_pipeline_once.py" >> "$PROJECT_DIR/logs/pipeline.log" 2>&1