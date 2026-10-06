
  
    

  create  table "vietnam_air_quality"."analytics_analytics"."fact_weather_hourly__dbt_tmp"
  
  
    as
  
  (
    SELECT * FROM "vietnam_air_quality"."analytics_staging"."stg_weather"
  );
  