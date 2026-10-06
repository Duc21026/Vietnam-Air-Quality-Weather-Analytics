
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id
from "vietnam_air_quality"."analytics_staging"."stg_weather"
where id is null



  
  
      
    ) dbt_internal_test