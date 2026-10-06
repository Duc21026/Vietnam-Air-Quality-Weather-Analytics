
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id as unique_field,
    count(*) as n_records

from "vietnam_air_quality"."analytics_staging"."stg_air_quality"
where id is not null
group by id
having count(*) > 1



  
  
      
    ) dbt_internal_test