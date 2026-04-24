--models/bronze/bronze_bookings.sql

SELECT * FROM {{ source('dlt_ingestion', 'bookings') }}