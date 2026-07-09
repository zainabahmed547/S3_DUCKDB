with source as (
    select * from {{ source('dlt_ingestion','bookings')}}
)
select
     cast(booking_id as varchar) as booking_id,
     cast(listing_id as bigint) as listing_id,
     cast(booking_date as date) as booking_date,
     cast(nights_booked as int) as nights_booked,
     cast(booking_amount as decimal(10,2)) as booking_amount,
     cast(cleaning_fee as decimal(10,2)) as cleaning_fee,
     cast(service_fee as decimal(10,2)) as service_fee,
     cast(booking_status as varchar) as booking_status,
from source