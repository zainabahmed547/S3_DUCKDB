with source as (
    select * from {{ source('dlt_ingestion','listings')}}
),
deduplicated as (
    select
        cast(listing_id as bigint) as listing_id,
        cast(host_id as bigint) as host_id,
        cast(property_type as varchar) as property_type,
        cast(room_type as varchar) as room_type,
        cast(city as varchar) as city,
        cast(country as varchar) as country,
        cast(accommodates as int) as accommodates,
        cast(bedrooms as int) as bedrooms,
        cast(bathrooms as int) as bathrooms,
        cast(price_per_night as decimal(10,2)) as price_per_night,
        row_number() over (partition by listing_id order by host_id) as row_num
    from source
)
select
    listing_id,
    host_id,
    property_type,
    room_type,
    city,
    country,
    accommodates,
    bedrooms,
    bathrooms,
    price_per_night
from deduplicated
where row_num = 1