
    
    

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


