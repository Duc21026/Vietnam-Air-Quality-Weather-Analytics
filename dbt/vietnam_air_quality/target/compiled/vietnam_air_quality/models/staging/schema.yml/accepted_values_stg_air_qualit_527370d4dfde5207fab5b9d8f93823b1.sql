
    
    

with all_values as (

    select
        parameter as value_field,
        count(*) as n_records

    from "vietnam_air_quality"."analytics_staging"."stg_air_quality"
    group by parameter

)

select *
from all_values
where value_field not in (
    'pm25','pm10','pm1','co','no2','o3','so2'
)


