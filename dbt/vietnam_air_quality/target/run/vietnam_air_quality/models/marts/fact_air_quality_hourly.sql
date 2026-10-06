
  
    

  create  table "vietnam_air_quality"."analytics_analytics"."fact_air_quality_hourly__dbt_tmp"
  
  
    as
  
  (
    SELECT * FROM "vietnam_air_quality"."analytics_intermediate"."int_hourly_air_quality"
  );
  