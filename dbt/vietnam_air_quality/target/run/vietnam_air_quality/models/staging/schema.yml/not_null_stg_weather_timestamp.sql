
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select timestamp
from "vietnam_air_quality"."analytics_staging"."stg_weather"
where timestamp is null



  
  
      
    ) dbt_internal_test