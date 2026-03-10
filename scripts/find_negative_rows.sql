select
  snapshot_ts,
  station_id,
  num_bikes_available,
  num_docks_available,
  is_installed,
  is_renting,
  is_returning
from raw.gbfs_station_status_snapshot
where num_bikes_available < 0
   or num_docks_available < 0
order by snapshot_ts desc
limit 25;
