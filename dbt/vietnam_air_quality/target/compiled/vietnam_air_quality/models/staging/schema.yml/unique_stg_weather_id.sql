
    
    

select
    id as unique_field,
    count(*) as n_records

from "vietnam_air_quality"."analytics_staging"."stg_weather"
where id is not null
group by id
having count(*) > 1


