
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select timestamp_utc
from "vietnam_air_quality"."analytics_staging"."stg_air_quality"
where timestamp_utc is null



  
  
      
    ) dbt_internal_test