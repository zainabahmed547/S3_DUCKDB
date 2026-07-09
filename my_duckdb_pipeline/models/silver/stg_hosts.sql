with source as (
    select * from {{ source('dlt_ingestion','hosts')}}
),
deduplicated as (  
   select  
      cast(host_id as bigint) as host_id,
      cast(host_name as varchar) as host_name,
      cast(host_since as date) as host_since_date,
      case
          when is_superhost in ('true', 't', '1') then true
          else false
          end as is_superhost,
      cast(response_rate as decimal(5,2)) / 100 as response_rate,

    --create a row number for unique host_id
      row_number() over (partition by host_id order by host_since) as row_num
    from source
)

--Only keep the appearance of each host
select * from deduplicated where row_num = 1