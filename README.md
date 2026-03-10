# City Mobility Ops

## Overview
City Mobility Ops is a near real time analytics project for Dublin bike share operations. It ingests live station snapshots, enriches them with weather, computes operational KPIs, and produces rebalancing recommendations that are easy to act on.

The goal is simple. Help ops teams spot stations that are about to go empty or full, understand when and why it happens, and decide where to move bikes next.

## Live status update
This section is meant to be refreshed whenever you generate new screenshots.

Latest snapshot time (UTC): 2026 03 10 19:33  
Stations captured: 116  
Service level now: 99
Empty stations now: 12 
Full stations now: 5 

How to refresh this section quickly:
1. Run the pipeline once.
2. Run the notebook cell that prints the current summary.
3. Copy the latest values here.

## Why this project exists
If a station is empty, riders cannot rent a bike.  
If a station is full, riders cannot return a bike.  

Both situations create complaints and reduce trust, especially at peak hours and in bad weather. This project treats it as an operations problem, not a guessing game.

## What I built
1. Near real time ingestion of Dublinbikes GBFS feeds into Postgres as timestamped snapshots
2. Weather ingestion using OpenWeather forecast data in metric units
3. Analytics views that compute station and city KPIs by hour
4. Data quality checks for sanity and freshness
5. A rebalancing recommender that pairs donors and receivers using proximity and available inventory
6. Matplotlib visual outputs saved as portfolio ready screenshots

## Data sources
1. Dublinbikes GBFS feeds via the GBFS discovery file
2. OpenWeather forecast endpoint for temperature, wind, and precipitation
3. Derived calendar features from timestamps such as hour, weekday, month

## KPIs
1. Empty rate  
Percent of snapshots where bikes available equals 0

2. Full rate  
Percent of snapshots where docks available equals 0

3. Service level  
Percent of snapshots where bikes available is at least 1 and docks available is at least 1

4. Volatility score  
Daily count of station state changes between healthy, empty, and full

## Data model
Raw layer stores snapshots and never overwrites history.
1. raw.gbfs_station_information_snapshot  
2. raw.gbfs_station_status_snapshot  
3. raw.weather_hourly  

Analytics layer is built as views for fast iteration.
1. analytics.dim_station  
2. analytics.fact_station_snapshot  
3. analytics.mart_station_hourly  
4. analytics.mart_city_hourly  
5. analytics.mart_station_daily_volatility  
6. analytics.bi_station_latest  
7. analytics.bi_station_hourly  

## Rebalancing recommender
The recommender turns analysis into action.
1. Receivers are stations that are empty or near empty.
2. Donors are stations that are full or near full.
3. Recommendations match donors to receivers using distance and available inventory.
4. Donor inventory is reduced after each move to avoid unrealistic over allocation.
5. If no donor is available within a distance cap, the receiver is flagged as unserved.

Outputs:
1. A table of suggested moves: receiver, donor, distance, bikes to move
2. A map style matplotlib plot showing donors, receivers, and arrow directions

## Screenshots
Add your latest screenshots here. These should be generated from the notebook and committed to the repo.

1. City health by hour  
docs/screenshots/city_health_hourly_2026/10/03_19:38.png

2. Empty risk stations  
docs/screenshots/empty_risk_stations_2026/10/03_19:38.png

3. Full risk stations  
docs/screenshots/full_risk_stations_2026/10/03_19:38.png

4. Rebalancing arrows map  
docs/screenshots/rebalance_arrows_2026/10/03_19:38.png

5. Rebalancing suggestions table  
docs/rebalancing_suggestions_top20_2026/10/03_19:38.csv

Tip: if you want the images to render directly on GitHub, use the image syntax below and replace the filenames with your latest run.

City health  
![City health](docs/screenshots/city_health_hourly_2026/10/03_19:38.png)

Empty risk stations  
![Empty risk stations](docs/screenshots/empty_risk_stations_2026/10/03_19:38.png)

Full risk stations  
![Full risk stations](docs/screenshots/full_risk_stations_2026/10/03_19:38.png)

Rebalancing arrows map  
![Rebalancing arrows](docs/screenshots/rebalance_arrows_2026/10/03_19:38.png)

## How to run locally
### Prerequisites
1. Python installed
2. Postgres running locally
3. A virtual environment created in .venv

### Environment variables
Create a local file at scripts/env_local.sh and keep it out of git.

Required variables:
1. DATABASE_URL
2. GBFS_ROOT_URL
3. GBFS_LANGUAGE
4. OWM_API_KEY
5. WEATHER_BASE_URL
6. WEATHER_CITY
7. WEATHER_COUNTRY

Example values:
DATABASE_URL=postgresql://postgres:<your_password>@localhost:5432/mobility  
GBFS_ROOT_URL=https://api.cyclocity.fr/contracts/dublin/gbfs/gbfs.json  
GBFS_LANGUAGE=fr  
WEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/forecast  
WEATHER_CITY=Dublin  
WEATHER_COUNTRY=IE  
OWM_API_KEY=<your_key>  

### Run the pipeline once
The pipeline does four things in order:
1. Ingest GBFS station snapshots
2. Ingest weather forecast points
3. Rebuild analytics views
4. Run quality checks

Run:
1. source .venv/bin/activate
2. source scripts/env_local.sh
3. python scripts/run_pipeline_once.py

### Generate plots and screenshots
Open the notebook in the notebooks folder, run the cells that:
1. Print the current snapshot status
2. Create and save the matplotlib screenshots into docs/screenshots
3. Export the top move recommendations into docs

## Quality checks
Quality checks are designed to fail loudly.
They validate:
1. No null station_id values in raw station status
2. No negative bikes or docks
3. Capacity sanity checks
4. Weather coverage in the fact table
5. Freshness of latest snapshot within a time window

Run:
python scripts/run_quality_checks.py

## Automation
A scheduled job runs the pipeline on a regular interval so the data stays fresh.
Logs are written to logs/pipeline.log.

For a portfolio run, a five minute schedule is usually enough to show near real time behaviour.

## Repository structure
1. src  
1.1 ingest  
1.2 transforms  
1.3 quality  
1.4 common  

2. scripts  
3. notebooks  
4. docs  
4.1 screenshots  
5. logs  

## Notes on interpretation
Service level is a useful health signal, but empty events tend to be the more common rider pain. Full events matter too, because they create the return problem. The rebalancing outputs are designed to handle both by moving bikes away from donor stations and toward receiver stations.

## Future improvements
1. Add a public holiday calendar table for better demand modelling
2. Replace views with a transformation framework for versioned models
3. Add a short term risk model for empty or full events, 30 to 60 minutes ahead
4. Add route batching so one donor can supply multiple receivers in a single run
5. Add a basemap layer or a richer map visual for presentation

## Contact
If you would like to discuss the approach or improvements, feel free to reach out.