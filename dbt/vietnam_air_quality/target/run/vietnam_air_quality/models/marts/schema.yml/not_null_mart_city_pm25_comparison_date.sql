
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date
from "vietnam_air_quality"."analytics_analytics"."mart_city_pm25_comparison"
where date is null



  
  
      
    ) dbt_internal_test