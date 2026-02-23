City Mobility Ops project brief
1) Product in one sentence

City Mobility Ops is a near real time view of Dublin bike station health that explains drivers, shows trends, and highlights short term risk of stations going empty or full.

2) Stakeholder and problem

Primary stakeholder is a mobility operations team that handles rebalancing.

They care about two things. Which stations are about to go empty or full, and where they should rebalance first.

The pain is simple. Riders complain when stations are empty or full, and the team needs a way to spot issues early, understand why they happen, and act before service drops.

3) Decisions the dashboard supports

The dashboard should support these decisions.

Which stations need attention in the next hour

When are the worst periods by area and time of day

Which stations need a long term fix, including capacity changes and rebalancing priority

4) Data sources

Dublinbikes GBFS feeds, station information and station status, discovered through the gbfs.json discovery file

Weather data with hourly variables, later joined to station snapshots

Calendar features generated in the pipeline, weekday, hour, month, and a public holiday flag

5) Refresh cadence and retention

Station status ingestion every five minutes

Station information ingestion once per day

Weather ingestion once per hour

Raw snapshots retained for at least thirty days

6) KPIs and definitions

Empty rate
Percent of snapshots where bikes available equals zero

Full rate
Percent of snapshots where docks available equals zero

Service level
Percent of snapshots where bikes available is at least one and docks available is at least one

Volatility score
Count of state changes per day, where state is healthy, empty, or full

7) First version deliverables

A pipeline that stores station status snapshots in a database

Analytics tables that compute hourly KPIs per station

A dashboard with an operations view plus reliability trends

A simple risk label for the next thirty to sixty minutes

8) Done means

Data loads run on schedule for forty eight hours with no manual fixes

Dashboard shows current station status and the ten worst stations by empty rate and full rate

KPI definitions match this brief and stay consistent across all pages

README explains the problem, the data, and the decisions supported in under ninety seconds of reading