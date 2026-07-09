with bookings as (
    select * from {{ ref('stg_bookings')}}
)
select
md5(cast(listing_id as varchar) || '_' || cast(date_trunc('month', booking_date) as varchar)) as monthly_performance_id,
listing_id,
date_trunc('month', booking_date) as performance_month,
--Aggregate Metrics
count(distinct booking_id) as total_bookings_received,
sum(nights_booked) as total_nights_occupied,
sum(booking_amount) as monthly_rental_revenue,
sum(cleaning_fee) as monthly_cleaning_revenue,
--Combined gross revenue
sum(booking_amount + cleaning_fee + service_fee) as total_monthly_gross_revenue,
--operational state flags
count(distinct case when booking_status = 'cancelled' then booking_id end) as total_bookings_cancelled

from bookings
group by 
listing_id, date_trunc('month', booking_date)