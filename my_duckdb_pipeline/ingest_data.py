import dlt
from dlt.sources.filesystem import filesystem, read_csv
from typing import Iterator, Any

@dlt.resource(
    name="listings",
    columns={
        "host_id": {"data_type": "bigint"},
        "property_type": {"data_type": "text"},
        "room_type": {"data_type": "text"},
        "city" : {"data_type": "text"},
        "country": {"data_type": "text"},
        "accommodates": {"data_type": "bigint"},
        "bedrooms": {"data_type": "bigint"},
        "bathrooms": {"data_type": "decimal"},
        "price_per_night": {"data_type": "decimal"},
        "created_at": {"data_type": "timestamp"},
    }
)
def get_listings() -> Iterator[dict]:
    files = filesystem(
        bucket_url="s3://snowbucketzee/source/",
        file_glob="**/listings.csv"
    ) | read_csv()
    for item in files:
        yield item

dlt.resource(
    name="bookings",
    columns={
        "booking_id": {"data_type": "bigint"},
        "listing_id": {"data_type": "bigint"},
        "booking_date": {"data_type": "date"},
        "nights_booked": {"data_type": "bigint"},
        "booking_amount": {"data_type": "decimal"},
        "cleaning_fee": {"data_type": "decimal"},
        "service_fee": {"data_type": "decimal"},
        "booking_status": {"data_type": "text"},
        "created_at": {"data_type": "timestamp"},
    }
)
def get_bookings() -> Iterator[dict]:
    files = filesystem(
        bucket_url="s3://snowbucketzee/source/",
        file_glob="**/bookings.csv"
    ) | read_csv()
    for item in files:
        yield item

dlt.resource(
    name="hosts",
    columns={
        "host_id": {"data_type": "bigint"},
        "host_name": {"data_type": "text"},
        "host_since": {"data_type": "date"},
        "is_superhost": {"data_type": "boolean"},
        "response_rate": {"data_type": "bigint"},
        "created_at": {"data_type": "timestamp"},
    }
)
def get_hosts() -> Iterator[dict]:
    files = filesystem(
        bucket_url="s3://snowbucketzee/source/",
        file_glob="**/hosts.csv"
    ) | read_csv()
    for item in files:
        yield item


@dlt.source
def airbnb_source():
    return [get_listings(), get_bookings(), get_hosts()]

# Load data into the pipeline
pipeline = dlt.pipeline(
    pipeline_name="ingest_pipeline",
    destination=dlt.destinations.duckdb("C:/Projects/S3_DUCKDB_PIPELINE/my_duckdb_pipeline/dev.duckdb"),
    dataset_name="bronze"
)

airbnb_source_instance = airbnb_source()
info = pipeline.run(airbnb_source_instance)

print("\n===== PIPELINE RESULTS =====")
print(info)

# Query the data to confirm it loaded
try:
    dataset = pipeline.dataset()
    tables = dataset.table_names()
    print(f"\n✅ Success! Tables created: {tables}")
    for table in tables:
        row_count = len(dataset[table].df())
        print(f"   - {table}: {row_count} rows")
except Exception as e:
    print(f"Error reading data: {e}")