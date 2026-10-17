
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        city as value_field,
        count(*) as n_records

    from "vietnam_air_quality"."analytics_analytics"."mart_city_pm25_comparison"
    group by city

)

select *
from all_values
where value_field not in (
    'Hanoi','Ho Chi Minh City'
)



  
  
      
    ) dbt_internal_test