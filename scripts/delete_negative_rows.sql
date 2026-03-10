delete from raw.gbfs_station_status_snapshot
where num_bikes_available < 0
   or num_docks_available < 0;
