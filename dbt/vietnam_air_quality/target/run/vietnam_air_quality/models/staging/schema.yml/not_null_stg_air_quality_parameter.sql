
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select parameter
from "vietnam_air_quality"."analytics_staging"."stg_air_quality"
where parameter is null



  
  
      
    ) dbt_internal_test