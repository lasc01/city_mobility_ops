create or replace view analytics.dim_station as
with ranked as (
  select
    snapshot_ts,
    station_id,
    name,
    lat,
    lon,
    capacity,
    row_number() over (
      partition by station_id
      order by snapshot_ts desc
    ) as rn
  from raw.gbfs_station_information_snapshot
)
select
  snapshot_ts as effective_ts,
  station_id,
  name,
  lat,
  lon,
  capacity
from ranked
where rn = 1
;

create or replace view analytics.fact_station_snapshot as
select
  s.snapshot_ts,
  (s.snapshot_ts at time zone 'Europe/Dublin') as snapshot_local_ts,
  date_trunc('hour', (s.snapshot_ts at time zone 'Europe/Dublin')) as snapshot_hour_local,
  date((s.snapshot_ts at time zone 'Europe/Dublin')) as snapshot_local_date,

  extract(isodow from (s.snapshot_ts at time zone 'Europe/Dublin'))::int as iso_dow,
  extract(hour from (s.snapshot_ts at time zone 'Europe/Dublin'))::int as hour_of_day,
  extract(month from (s.snapshot_ts at time zone 'Europe/Dublin'))::int as month_of_year,

  s.station_id,
  d.name,
  d.lat,
  d.lon,
  d.capacity,

  s.num_bikes_available,
  s.num_docks_available,
  s.is_installed,
  s.is_renting,
  s.is_returning,
  s.last_reported,

  case
    when s.num_bikes_available = 0 then 'empty'
    when s.num_docks_available = 0 then 'full'
    else 'healthy'
  end as station_state,

  w.temperature_c,
  w.precipitation_mm,
  w.wind_speed,
  w.weather_code

from raw.gbfs_station_status_snapshot s
left join analytics.dim_station d
  on d.station_id = s.station_id

left join lateral (
  select
    wh.temperature_c,
    wh.precipitation_mm,
    wh.wind_speed,
    wh.weather_code
  from raw.weather_hourly wh
  order by abs(extract(epoch from age(wh.hour_ts, s.snapshot_ts))) asc
  limit 1
) w on true
;

create or replace view analytics.mart_station_hourly as
select
  station_id,
  snapshot_hour_local,
  count(*) as snapshot_count,

  avg(num_bikes_available)::numeric(10,2) as avg_bikes_available,
  avg(num_docks_available)::numeric(10,2) as avg_docks_available,

  avg(case when num_bikes_available = 0 then 1 else 0 end)::numeric(10,4) as empty_rate,
  avg(case when num_docks_available = 0 then 1 else 0 end)::numeric(10,4) as full_rate,
  avg(case when num_bikes_available > 0 and num_docks_available > 0 then 1 else 0 end)::numeric(10,4) as service_level,

  avg(temperature_c)::numeric(10,2) as avg_temperature_c,
  sum(precipitation_mm)::numeric(10,2) as total_precipitation_mm,
  avg(wind_speed)::numeric(10,2) as avg_wind_speed

from analytics.fact_station_snapshot
group by station_id, snapshot_hour_local
;

create or replace view analytics.mart_city_hourly as
select
  snapshot_hour_local,
  count(distinct station_id) as station_count,
  count(*) as snapshot_count,

  avg(case when num_bikes_available = 0 then 1 else 0 end)::numeric(10,4) as empty_rate,
  avg(case when num_docks_available = 0 then 1 else 0 end)::numeric(10,4) as full_rate,
  avg(case when num_bikes_available > 0 and num_docks_available > 0 then 1 else 0 end)::numeric(10,4) as service_level,

  avg(temperature_c)::numeric(10,2) as avg_temperature_c,
  sum(precipitation_mm)::numeric(10,2) as total_precipitation_mm,
  avg(wind_speed)::numeric(10,2) as avg_wind_speed

from analytics.fact_station_snapshot
group by snapshot_hour_local
;

create or replace view analytics.mart_station_daily_volatility as
with t as (
  select
    station_id,
    snapshot_local_date,
    snapshot_ts,
    station_state,
    lag(station_state) over (
      partition by station_id, snapshot_local_date
      order by snapshot_ts
    ) as prev_state
  from analytics.fact_station_snapshot
)
select
  station_id,
  snapshot_local_date,
  sum(
    case
      when prev_state is null then 0
      when station_state <> prev_state then 1
      else 0
    end
  ) as volatility_score,
  count(*) as snapshot_count
from t
group by station_id, snapshot_local_date
;

create or replace view analytics.bi_station_latest as
with latest_ts as (
  select max(snapshot_ts) as snapshot_ts
  from raw.gbfs_station_status_snapshot
),
latest_rows as (
  select f.*
  from analytics.fact_station_snapshot f
  join latest_ts t
    on f.snapshot_ts = t.snapshot_ts
)
select
  station_id,
  name,
  lat,
  lon,
  capacity,
  snapshot_ts,
  snapshot_local_ts,
  station_state,
  num_bikes_available,
  num_docks_available,
  temperature_c,
  precipitation_mm,
  wind_speed,
  weather_code,
  case when num_bikes_available = 0 then 1 else 0 end as is_empty,
  case when num_docks_available = 0 then 1 else 0 end as is_full,
  case when num_bikes_available > 0 and num_docks_available > 0 then 1 else 0 end as is_healthy
from latest_rows
;

create or replace view analytics.bi_station_hourly as
select
  h.station_id,
  d.name,
  d.lat,
  d.lon,
  d.capacity,
  h.snapshot_hour_local,
  h.snapshot_count,
  h.avg_bikes_available,
  h.avg_docks_available,
  h.empty_rate,
  h.full_rate,
  h.service_level,
  h.avg_temperature_c,
  h.total_precipitation_mm,
  h.avg_wind_speed
from analytics.mart_station_hourly h
left join analytics.dim_station d
  on d.station_id = h.station_id
;