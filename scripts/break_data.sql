insert into raw.gbfs_station_status_snapshot
(snapshot_ts, last_updated, ttl, station_id, num_bikes_available, num_docks_available, is_installed, is_renting, is_returning, last_reported, payload)
values
(current_timestamp, 0, null, 'test_station', -1, 0, 1, 1, 1, 0, '{}'::jsonb);
