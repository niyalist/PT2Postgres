-- Run this with psql to create all tables

CREATE SCHEMA IF NOT EXISTS pt2018;
\i schemas/sql/a1_population_by_age_and_gender.sql
\i schemas/sql/a2_population_by_employment_type.sql
\i schemas/sql/b1_population_by_age_and_gender.sql
\i schemas/sql/b1_trip_stats_by_purpose_age_gender.sql
\i schemas/sql/b2_population_by_employment_age.sql
\i schemas/sql/b2_trip_stats_by_purpose_employment_age.sql
\i schemas/sql/b3_trip_count_by_vehicle_and_purpose.sql
\i schemas/sql/b4_population_by_time_slot.sql
\i schemas/sql/c1_trip_origin_dest_by_mode_and_purpose.sql
\i schemas/sql/c2_trip_origin_dest_by_time_and_purpose.sql
\i schemas/sql/c3_trip_origin_dest_by_mode_and_time.sql
\i schemas/sql/c4_trip_origin_dest_by_facility_and_mode.sql
\i schemas/sql/d1_trip_od_by_purpose_and_mode.sql
\i schemas/sql/e1_trip_by_station_and_terminal_mode.sql
\i schemas/sql/e2_mean_travel_time_by_mode_and_od.sql
\i schemas/sql/e3_parking_count_by_location_and_purpose.sql
\i schemas/sql/e4_zone_code_to_area_lookup.sql