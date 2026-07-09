with bookings as (
    select * from {{ ref('stg_bookings')}}
)
select
    booking_id,
    listing_id,
    booking_date,
    nights_booked,
    booking_status,
    booking_amount,
    cleaning_fee,
    service_fee,
    --Total Gross Revenue
    (booking_amount + cleaning_fee + service_fee) as total_gross_revenue
from bookings