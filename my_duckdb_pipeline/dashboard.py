import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

#-----------------------------------------
# CONFIGURATION & DATABASE CONNECTION
#-----------------------------------------
st.set_page_config(page_title="Analytics Dashboard", layout="wide")
DB_PATH = "C:/Projects/S3_DUCKDB_PIPELINE/my_duckdb_pipeline/dev.duckdb"

def run_query(query):
    """Helper function to run SQL against our DuckDB database."""
    try:
        conn = duckdb.connect(database=DB_PATH, read_only=True)
        df = conn.execute(query).df()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()
    
#-------------------------------------------
# DASHBOARD HEADER
#-------------------------------------------
st.title("Airbnb Marketplace Performance Dashboard")
st.markdown("Surfacing marketplace health and operational trends directly from our **Gold Analytical Layer** (star schema).")
st.markdown("---")

#------------------------------------------
# PRIMARY METRICS
#------------------------------------------
kpi_query = """
select
    count(distinct booking_id) as total_bookings,
    sum(total_gross_revenue) as total_revenue,
    sum(service_fee) as platform_revenue,
    avg(booking_amount / nullif(nights_booked, 0)) as avg_nightly_rate
    from gold.fct_bookings
    where booking_status = 'confirmed'
"""
kpi_df = run_query(kpi_query)

if not kpi_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Gross Revenue", value=f"${kpi_df['total_revenue'][0]:,.2f}")
    with col2:
        st.metric(label="Confirmed Bookings", value=f"{kpi_df['total_bookings'][0]:,}")
    with col3:
        st.metric(label="Platform Revenue", value=f"${kpi_df['platform_revenue'][0]:,.2f}")
    with col4:
        st.metric(label="Average Nightly Rate", value=f"${kpi_df['avg_nightly_rate'][0]:.2f}")

st.markdown("---")


#---------------------------------------------
# PROPERTY TYPE ANALYSIS
#----------------------------------------------
st.header("Property Mix Analysis")

property_query = """
    select
    l.room_type,
    count(b.booking_id) as total_bookings,
    sum(b.total_gross_revenue) as revenue
from gold.fct_bookings b
left join gold.dim_listings l on b.listing_id = l.listing_id
where b.booking_status = 'confirmed'
group by 1
order by revenue desc
"""
property_df = run_query(property_query)

if not property_df.empty:
    fig_prop = px.bar(
        property_df,
        x='revenue',
        y='room_type',
        orientation='h',
        title='Revenue Contribution by Room Type',
        labels={'revenue': 'Total Revenue ($)', 'room_type': 'Room Type'},
        color='revenue',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_prop, use_container_width=True)
     
st.markdown("---")
#---------------------------------------------
# REGIONAL MONTHLY TRENDS & CANCELLATION ANALYSIS
#---------------------------------------------
st.header("Regional Growth Trends")
st.markdown("Leveraging pre-aggregated snapshots to isolate growth trends and tracking occupancy over time.")

monthly_query = """
   with top_five_cities as (
       select
           l.city,
           sum(b.total_monthly_gross_revenue) as total_revenue
        from gold.fct_monthly_listing_performance b
           left join gold.dim_listings l on b.listing_id = l.listing_id
         group by 1
         order by total_revenue desc
           limit 5
    )

   select
       l.city,
       b.performance_month,
       sum(b.total_monthly_gross_revenue) as monthly_revenue,
       sum(b.total_nights_occupied) as nights_occupied,
       sum(b.total_bookings_cancelled) as cancellations
    from gold.fct_monthly_listing_performance b
    left join gold.dim_listings l on b.listing_id = l.listing_id
    where l.city in (select city from top_five_cities)
    group by 1,2
    order by performance_month asc
    """
monthly_df = run_query(monthly_query)

if not monthly_df.empty:
    monthly_df['performance_month'] = pd.to_datetime(monthly_df['performance_month'])

    # Revenue and Occupancy Charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_rev = px.line(
            monthly_df,
            x='performance_month',
            y='monthly_revenue',
            color='city',
            title='Gross Monthly Revenue by City',
            labels={'monthly_revenue': 'Revenue ($)', 'performance_month': 'Month',},
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_chart2:
        fig_occ = px.bar(
            monthly_df,
            x='performance_month',
            y='nights_occupied',
            color='city',
            title='Total Nights Occupied',
            labels={'nights_occupied': 'Nights Booked', 'performance_month': 'Month',},
        )
        st.plotly_chart(fig_occ, use_container_width=True)

    # Cancellation Analysis
    st.markdown("### Cancellation Trends")
    fig_cancel = px.line(
        monthly_df,
        x='performance_month',
        y='cancellations',
        color='city',
        title='Monthly Cancellations by City',
        labels={'cancellations': 'Cancelled Bookings', 'performance_month': 'Month',},
        line_dash= 'city'
    )
    st.plotly_chart(fig_cancel, use_container_width=True)

st.markdown("---")


#---------------------------------------------
# INSIGHTS AND RECOMMENDATIONS
#---------------------------------------------
st.header("Analytical Insights & Recommendations")
st.markdown("Contextualising warehouse performance metrics into structural business choices")

#Compute key ratios dynamically
total_revenue = kpi_df['total_revenue'][0]
private_room_revenue = property_df[property_df['room_type'] == 'Private room']['revenue'].values[0]
private_room_pct = (private_room_revenue/total_revenue) * 100

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.subheader("Inventory & Marketplace Optimization")
    st.markdown(
        f"""
        * **Private Room Demand Density:** Private rooms generate approximately **{private_room_pct:.1f}%** of gross platform revenue. While *Entire Homes* maintain a high absolute nightly margin, customer choice leans heavily toward cost-effective private space inventory.
        * **Strategic Recommendation:** Adjust supply acquisition targeting. The engineering pipeline's inventory mix highlights a clear commercial opportunity to recruit and onboard more single-room hosts to fulfill consistent core consumer volumes.
        """
    )

    with col_ins2:
        st.subheader("Seasonality and Operational Risk Protection")
        st.markdown(
            """
            * **Cancellation Spikes vs Demand:** Comparing the *Cancellations* trend line with the *Nights Occupied* chart reveals an operational vulnerability: regional booking churn escalates drastically in tandem with high-season demand surges.
            * **Strategic Recommendation:** Implement staggered, automated strict cancellation windows during peak seasons (e.g., Q2/Q3 vacation months) inside volatile regional cohorts like *Lake Jason* or *Josemouth* to insulate hosts from short-notice revenue loss.
            """

        )  