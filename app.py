# ============================================================
# OLA RIDE INSIGHTS
# Interactive Data Analytics Dashboard
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Ola Ride Insights",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. ASSETS (images taken from the Ola slides)
# ============================================================

import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"


def image_uri(file_name):
    """Return an image as a base64 data URI, or None if the file is missing."""
    path = ASSETS / file_name
    if not path.exists():
        return None
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{encoded}"


SVG_SHAPES = {
    "database": (
        "<ellipse cx='12' cy='5' rx='8' ry='3'/>"
        "<path d='M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5'/>"
        "<path d='M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3'/>"
    ),
    "chart": (
        "<rect x='4' y='12' width='4' height='8' rx='1'/>"
        "<rect x='10' y='6' width='4' height='14' rx='1'/>"
        "<rect x='16' y='3' width='4' height='17' rx='1'/>"
    ),
}


def icon_uri(spec):
    """PNG file name from the slides, or 'svg:<shape>:<colour>' for drawn icons."""
    if spec.startswith("svg:"):
        _, shape, colour = spec.split(":", 2)
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
            f"stroke='{colour}' stroke-width='1.5' stroke-linecap='round' "
            f"stroke-linejoin='round'>{SVG_SHAPES[shape]}</svg>"
        )
        return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    return image_uri(spec)


# Menu: (label, normal icon, icon when selected)
NAV_ITEMS = [
    ("Overall",      "image5.png",  "image15.png"),
    ("Vehicle Type", "image24.png", "image31.png"),
    ("Revenue",      "image2.png",  "image11.png"),
    ("Cancellation", "image13.png", "image18.png"),
    ("Ratings",      "image19.png", "image28.png"),
    ("SQL Queries",  "svg:database:#BFBFBF", "svg:database:#FFFFFF"),
    ("Power BI",     "svg:chart:#BFBFBF",    "svg:chart:#FFFFFF"),
]


def build_nav_css():
    """One CSS rule per menu item, so each item shows its own icon."""
    rules = []
    for position, (_, normal_icon, selected_icon) in enumerate(NAV_ITEMS, start=1):
        base = (
            '[data-testid="stSidebar"] div[role="radiogroup"] '
            f"> label:nth-of-type({position})"
        )
        normal_uri = icon_uri(normal_icon)
        selected_uri = icon_uri(selected_icon)
        if normal_uri:
            rules.append(f"{base} {{ background-image: url({normal_uri}); }}")
        if selected_uri:
            rules.append(
                f"{base}:has(input:checked) {{ background-image: url({selected_uri}); }}"
            )
    return "\n".join(rules)


# ============================================================
# 3. CUSTOM CSS - OLA DASHBOARD THEME
# ============================================================

THEME_CSS = """
<style>

/* Main dashboard background */
.stApp {
    background-color: #F4F6F8;
}

/* Main headings */
h1, h2, h3 {
    color: #20252B;
    font-weight: 700;
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E1E5E9;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

[data-testid="stMetricValue"] {
    color: #20252B;
    font-weight: 700;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

/* ---------- SIDEBAR (matches the Ola slide) ---------- */

[data-testid="stSidebar"] {
    background-color: #262626;
}

/* Remove the default padding so the menu bars run edge to edge */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 0 !important;
}

/* One menu row */
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    height: 64px !important;
    margin: 0 !important;
    padding: 0 12px 0 74px !important;
    border: none !important;
    border-radius: 0 !important;
    background-color: transparent !important;
    background-repeat: no-repeat !important;
    background-position: 18px center !important;
    background-size: 40px 40px !important;
    cursor: pointer;
}

/* Hide the round radio button itself */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Menu text: light grey, always visible */
[data-testid="stSidebar"] div[role="radiogroup"] > label,
[data-testid="stSidebar"] div[role="radiogroup"] > label * {
    color: #BFBFBF !important;
    font-size: 17px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #333333 !important;
}

/* Selected menu row: green bar with white text */
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background-color: #92D050 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked),
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

__NAV_RULES__

</style>
"""

st.markdown(
    THEME_CSS.replace("__NAV_RULES__", build_nav_css()),
    unsafe_allow_html=True
)


# ============================================================
# 4. DATABASE CONNECTION (automatic, no login box)
# ============================================================

@st.cache_resource
def create_db_engine(host, port, username, password, database):

    encoded_password = quote_plus(password)

    connection_url = (
        f"mysql+pymysql://{username}:{encoded_password}"
        f"@{host}:{port}/{database}"
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


def read_mysql_settings():
    """Read MySQL details from .streamlit/secrets.toml (kept out of GitHub)."""
    try:
        config = st.secrets["mysql"]
        return {
            "host": config.get("host", "localhost"),
            "port": config.get("port", "3306"),
            "username": config.get("username", "root"),
            "password": config["password"],
            "database": config.get("database", "ola_db"),
        }
    except Exception:
        return None


# ============================================================
# 5. SIDEBAR: LOGO
# ============================================================

logo_icon = image_uri("image17.png")
logo_text = image_uri("image9.png")

if logo_icon and logo_text:
    st.sidebar.markdown(
        f"""
        <div style="display:flex; align-items:center; padding:6px 16px 14px 0;">
            <img src="{logo_icon}" style="width:84px; height:84px;">
            <img src="{logo_text}" style="width:104px; margin-left:2px;">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown("## 🚕 OLA")


# ============================================================
# 5. DATABASE LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_data(_engine):

    query = """
    SELECT *
    FROM ola_rides
    """

    data = pd.read_sql(
        text(query),
        _engine
    )

    data["Ride_Date"] = pd.to_datetime(
        data["Ride_Date"]
    )

    data["Date"] = pd.to_datetime(
        data["Date"]
    )

    return data


# ============================================================
# 6. CONNECT TO THE DATABASE
# ============================================================

mysql_settings = read_mysql_settings()
sqlite_file = BASE_DIR / "ola_rides.db"

if mysql_settings:

    engine = create_db_engine(**mysql_settings)

elif sqlite_file.exists():

    # Fallback used when the app is deployed online
    engine = create_engine(f"sqlite:///{sqlite_file}")

else:

    st.error(
        "Database settings not found. Create the file "
        ".streamlit/secrets.toml next to app.py with your MySQL details."
    )
    st.stop()

try:

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

except Exception as e:

    st.error(f"Could not connect to the database: {e}")
    st.stop()


# ============================================================
# 7. LOAD DATA
# ============================================================

try:

    df = load_data(engine)

    if df.empty:
        st.error("The database table contains no records.")
        st.stop()

except Exception as e:

    st.error(f"Unable to load data: {e}")
    st.stop()


# ============================================================
# 8. DATA VALIDATION
# ============================================================

required_columns = [
    "Booking_ID",
    "Booking_Status",
    "Vehicle_Type",
    "Booking_Value",
    "Ride_Distance",
    "Ride_Date",
    "Hour",
    "Driver_Ratings",
    "Customer_Rating",
    "Payment_Method",
    "Customer_Cancel_Reason",
    "Driver_Cancel_Reason",
    "Success_Booking_Value",
    "Is_Success",
    "Is_Cancelled"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        f"Missing database columns: {missing_columns}"
    )

    st.stop()


# ============================================================
# 9. FILTERS (top of the page, inside a collapsible box)
# ============================================================

min_date = df["Ride_Date"].min().date()

max_date = df["Ride_Date"].max().date()

vehicle_options = sorted(
    df["Vehicle_Type"].dropna().unique()
)

with st.expander("🔎 Filters: date range and vehicle type"):

    filter_col1, filter_col2 = st.columns([1, 2])

    with filter_col1:

        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    with filter_col2:

        selected_vehicles = st.multiselect(
            "Select Vehicle Type",
            vehicle_options,
            default=vehicle_options
        )


if len(date_range) == 2:

    start_date, end_date = date_range

else:

    start_date = date_range[0]
    end_date = date_range[0]


filtered_df = df[
    (df["Ride_Date"].dt.date >= start_date) &
    (df["Ride_Date"].dt.date <= end_date) &
    (df["Vehicle_Type"].isin(selected_vehicles))
].copy()


if filtered_df.empty:

    st.warning("No records found for the selected filters.")
    st.stop()

# ============================================================
# 10. COMMON METRICS
# ============================================================

total_bookings = len(filtered_df)

successful_df = filtered_df[
    filtered_df["Booking_Status"] == "Success"
]

cancelled_df = filtered_df[
    filtered_df["Is_Cancelled"] == 1
]

successful_bookings = len(successful_df)

cancelled_bookings = len(cancelled_df)

success_rate = (
    successful_bookings / total_bookings * 100
    if total_bookings > 0 else 0
)

total_revenue = successful_df["Booking_Value"].sum()


# ============================================================
# 11. DASHBOARD NAVIGATION (sidebar menu with icons)
# ============================================================

page = st.sidebar.radio(
    "Navigate Dashboard",
    [label for label, _, _ in NAV_ITEMS],
    label_visibility="collapsed"
)


# ============================================================
# SQL HELPER (used by the SQL Queries page)
# ============================================================

@st.cache_data(ttl=300)
def run_query(_engine, sql, params=None):

    return pd.read_sql(
        text(sql),
        _engine,
        params=params
    )


# ============================================================
# PAGE 1: OVERALL DASHBOARD
# ============================================================

if page == "Overall":

    st.title("📊 Overall Ride Insights")

    st.markdown(
        "Analysis of Ola ride bookings for July 2024."
    )

    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Bookings",
        f"{total_bookings:,}"
    )

    col2.metric(
        "Successful Bookings",
        f"{successful_bookings:,}"
    )

    col3.metric(
        "Cancelled Bookings",
        f"{cancelled_bookings:,}"
    )

    col4.metric(
        "Success Rate",
        f"{success_rate:.2f}%"
    )

    st.markdown("---")

    # BOOKING STATUS DISTRIBUTION

    col1, col2 = st.columns(2)

    status_data = (
        filtered_df["Booking_Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = [
        "Booking_Status",
        "Bookings"
    ]

    with col1:

        st.subheader("Booking Status Distribution")

        fig = px.pie(
            status_data,
            names="Booking_Status",
            values="Bookings",
            hole=0.45,
            title="Distribution of Booking Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # DAILY RIDE VOLUME

    daily_data = (
        filtered_df.groupby("Ride_Date")
        .size()
        .reset_index(name="Total_Rides")
    )

    with col2:

        st.subheader("Daily Ride Volume")

        fig = px.line(
            daily_data,
            x="Ride_Date",
            y="Total_Rides",
            markers=True,
            title="Daily Ride Booking Trend"
        )

        fig.update_layout(
            xaxis_title="Ride Date",
            yaxis_title="Number of Bookings"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # HOURLY DEMAND

    st.subheader("Hourly Ride Demand")

    hourly_data = (
        filtered_df.groupby("Hour")
        .size()
        .reset_index(name="Total_Rides")
        .sort_values("Hour")
    )

    fig = px.bar(
        hourly_data,
        x="Hour",
        y="Total_Rides",
        title="Ride Bookings by Hour of Day",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Total Bookings"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 2: VEHICLE TYPE ANALYSIS
# ============================================================

elif page == "Vehicle Type":

    st.title("🚘 Vehicle Type Analysis")

    st.markdown(
        "Compare booking values and ride distances "
        "across different vehicle categories."
    )

    vehicle_data = (
        filtered_df.groupby("Vehicle_Type")
        .agg(
            Total_Booking_Value=(
                "Booking_Value", "sum"
            ),
            Success_Booking_Value=(
                "Success_Booking_Value", "sum"
            ),
            Avg_Distance_Travelled=(
                "Ride_Distance",
                lambda x: x[
                    filtered_df.loc[x.index, "Is_Success"] == 1
                ].mean()
            ),
            Total_Distance_Travelled=(
                "Ride_Distance", "sum"
            )
        )
        .reset_index()
        .sort_values(
            "Total_Distance_Travelled",
            ascending=False
        )
    )

    vehicle_data[
        "Avg_Distance_Travelled"
    ] = vehicle_data[
        "Avg_Distance_Travelled"
    ].round(2)

    # VEHICLE COMPARISON TABLE

    st.subheader("Vehicle Performance Summary")

    st.dataframe(
        vehicle_data,
        use_container_width=True
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            vehicle_data,
            x="Vehicle_Type",
            y="Total_Booking_Value",
            title="Total Booking Value by Vehicle",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            vehicle_data,
            x="Vehicle_Type",
            y="Success_Booking_Value",
            title="Successful Booking Value by Vehicle",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # DISTANCE COMPARISON

    st.subheader("Vehicle Distance Comparison")

    fig = px.bar(
        vehicle_data,
        x="Vehicle_Type",
        y="Total_Distance_Travelled",
        title="Total Distance Travelled by Vehicle",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # TOP FIVE VEHICLES

    top_vehicles = vehicle_data.nlargest(
        5,
        "Total_Distance_Travelled"
    )

    st.subheader("Top 5 Vehicle Types by Distance")

    fig = px.bar(
        top_vehicles,
        x="Vehicle_Type",
        y="Total_Distance_Travelled",
        title="Top 5 Vehicles by Total Distance",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 3: REVENUE ANALYSIS
# ============================================================

elif page == "Revenue":

    st.title("💰 Revenue Analysis")

    st.markdown(
        "Revenue analysis based on successful rides only."
    )

    revenue = successful_df["Booking_Value"].sum()

    successful_rides = len(successful_df)

    average_booking_value = (
        revenue / successful_rides
        if successful_rides > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Revenue",
        f"₹{revenue:,.0f}"
    )

    col2.metric(
        "Successful Rides",
        f"{successful_rides:,}"
    )

    col3.metric(
        "Average Booking Value",
        f"₹{average_booking_value:,.2f}"
    )

    st.markdown("---")

    # REVENUE BY PAYMENT METHOD

    payment_data = (
        successful_df.groupby("Payment_Method")
        .agg(
            Revenue=("Booking_Value", "sum"),
            Rides=("Booking_ID", "count")
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Revenue by Payment Method")

        fig = px.bar(
            payment_data,
            x="Payment_Method",
            y="Revenue",
            title="Revenue Contribution by Payment Method",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("Payment Method Revenue Share")

        fig = px.pie(
            payment_data,
            names="Payment_Method",
            values="Revenue",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # TOP CUSTOMERS

    st.subheader("Top 5 Customers by Booking Value")

    customer_data = (
        successful_df.groupby("Customer_ID")
        ["Booking_Value"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "Booking_Value": "Total_Booking_Value"
            }
        )
        .sort_values(
            "Total_Booking_Value",
            ascending=False
        )
        .head(5)
    )

    fig = px.bar(
        customer_data,
        x="Customer_ID",
        y="Total_Booking_Value",
        title="Top 5 Customers by Successful Booking Value",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # DAILY DISTANCE

    st.subheader("Daily Ride Distance")

    daily_distance = (
        filtered_df.groupby("Ride_Date")
        .agg(
            Total_Distance=("Ride_Distance", "sum"),
            Avg_Distance=(
                "Ride_Distance",
                lambda x: x[
                    filtered_df.loc[x.index, "Is_Success"] == 1
                ].mean()
            )
        )
        .reset_index()
    )

    fig = px.line(
        daily_distance,
        x="Ride_Date",
        y="Total_Distance",
        markers=True,
        title="Total Ride Distance by Day"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 4: CANCELLATION ANALYSIS
# ============================================================

elif page == "Cancellation":

    st.title("❌ Cancellation Analysis")

    st.markdown(
        "Understand customer and driver cancellation patterns."
    )

    customer_cancelled = filtered_df[
        filtered_df["Booking_Status"] == "Canceled by Customer"
    ]

    driver_cancelled = filtered_df[
        filtered_df["Booking_Status"] == "Canceled by Driver"
    ]

    not_found = filtered_df[
        filtered_df["Booking_Status"] == "Driver Not Found"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customer Cancellations",
        f"{len(customer_cancelled):,}"
    )

    col2.metric(
        "Driver Cancellations",
        f"{len(driver_cancelled):,}"
    )

    col3.metric(
        "Driver Not Found",
        f"{len(not_found):,}"
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # CUSTOMER CANCELLATION REASONS

    customer_reasons = (
        customer_cancelled[
            "Customer_Cancel_Reason"
        ]
        .dropna()
        .value_counts()
        .reset_index()
    )

    customer_reasons.columns = [
        "Reason",
        "Cancellations"
    ]

    with col1:

        st.subheader("Customer Cancellation Reasons")

        if not customer_reasons.empty:

            fig = px.bar(
                customer_reasons,
                x="Reason",
                y="Cancellations",
                title="Reasons for Customer Cancellations",
                text_auto=True
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No customer cancellation reasons available.")

    # DRIVER CANCELLATION REASONS

    driver_reasons = (
        driver_cancelled[
            "Driver_Cancel_Reason"
        ]
        .dropna()
        .value_counts()
        .reset_index()
    )

    driver_reasons.columns = [
        "Reason",
        "Cancellations"
    ]

    with col2:

        st.subheader("Driver Cancellation Reasons")

        if not driver_reasons.empty:

            fig = px.bar(
                driver_reasons,
                x="Reason",
                y="Cancellations",
                title="Reasons for Driver Cancellations",
                text_auto=True
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No driver cancellation reasons available.")

    # CANCELLATION DISTRIBUTION

    cancellation_data = pd.DataFrame({
        "Cancellation Type": [
            "Customer Cancelled",
            "Driver Cancelled",
            "Driver Not Found"
        ],
        "Bookings": [
            len(customer_cancelled),
            len(driver_cancelled),
            len(not_found)
        ]
    })

    st.subheader("Cancellation Category Comparison")

    fig = px.pie(
        cancellation_data,
        names="Cancellation Type",
        values="Bookings",
        hole=0.4
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 5: RATINGS ANALYSIS
# ============================================================

elif page == "Ratings":

    st.title("⭐ Ratings Analysis")

    st.markdown(
        "Evaluate customer satisfaction and driver performance."
    )

    driver_ratings = filtered_df[
        "Driver_Ratings"
    ].dropna()

    customer_ratings = filtered_df[
        "Customer_Rating"
    ].dropna()

    avg_driver_rating = (
        driver_ratings.mean()
        if not driver_ratings.empty else 0
    )

    avg_customer_rating = (
        customer_ratings.mean()
        if not customer_ratings.empty else 0
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Average Driver Rating",
        f"{avg_driver_rating:.2f} / 5"
    )

    col2.metric(
        "Average Customer Rating",
        f"{avg_customer_rating:.2f} / 5"
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # DRIVER RATING DISTRIBUTION

    with col1:

        st.subheader("Driver Rating Distribution")

        if not driver_ratings.empty:

            fig = px.histogram(
                driver_ratings,
                x="Driver_Ratings",
                nbins=10,
                title="Distribution of Driver Ratings"
            )

            fig.update_layout(
                xaxis_title="Driver Rating",
                yaxis_title="Number of Rides"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No driver ratings available.")

    # CUSTOMER RATING DISTRIBUTION

    with col2:

        st.subheader("Customer Rating Distribution")

        if not customer_ratings.empty:

            fig = px.histogram(
                customer_ratings,
                x="Customer_Rating",
                nbins=10,
                title="Distribution of Customer Ratings"
            )

            fig.update_layout(
                xaxis_title="Customer Rating",
                yaxis_title="Number of Rides"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No customer ratings available.")

    # VEHICLE-WISE RATING COMPARISON

    rating_comparison = (
        filtered_df.groupby("Vehicle_Type")
        .agg(
            Avg_Driver_Rating=(
                "Driver_Ratings", "mean"
            ),
            Avg_Customer_Rating=(
                "Customer_Rating", "mean"
            )
        )
        .reset_index()
        .round(2)
    )

    st.subheader("Driver vs Customer Ratings by Vehicle")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=rating_comparison["Vehicle_Type"],
            y=rating_comparison["Avg_Driver_Rating"],
            name="Driver Rating"
        )
    )

    fig.add_trace(
        go.Bar(
            x=rating_comparison["Vehicle_Type"],
            y=rating_comparison["Avg_Customer_Rating"],
            name="Customer Rating"
        )
    )

    fig.update_layout(
        title="Average Ratings by Vehicle Type",
        xaxis_title="Vehicle Type",
        yaxis_title="Average Rating",
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Vehicle-wise Rating Summary")

    st.dataframe(
        rating_comparison,
        use_container_width=True
    )


# ============================================================
# PAGE 6: SQL QUERIES AND SEARCH
# ============================================================

elif page == "SQL Queries":

    st.title("🗄️ SQL Query Results")

    st.markdown(
        "Answers to the 10 project SQL questions, "
        "run live on the database."
    )

    st.caption(
        "These queries run on the full database, "
        "so the date and vehicle filters above do not apply here."
    )

    SQL_QUESTIONS = {
        "1. Retrieve all successful bookings": """
SELECT *
FROM ola_rides
WHERE Booking_Status = 'Success'""",

        "2. Average ride distance for each vehicle type": """
SELECT Vehicle_Type,
       ROUND(AVG(Ride_Distance), 2) AS Avg_Ride_Distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY Avg_Ride_Distance DESC""",

        "3. Total number of rides cancelled by customers": """
SELECT COUNT(*) AS Cancelled_By_Customers
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer'""",

        "4. Top 5 customers with the most rides": """
SELECT Customer_ID,
       COUNT(*) AS Total_Rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY Total_Rides DESC, Customer_ID
LIMIT 5""",

        "5. Rides cancelled by drivers (personal and car issues)": """
SELECT COUNT(*) AS Driver_Cancel_Personal_Car
FROM ola_rides
WHERE Driver_Cancel_Reason = 'Personal & Car related issue'""",

        "6. Max and min driver rating for Prime Sedan": """
SELECT MAX(Driver_Ratings) AS Max_Driver_Rating,
       MIN(Driver_Ratings) AS Min_Driver_Rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan'""",

        "7. All rides paid using UPI": """
SELECT *
FROM ola_rides
WHERE Payment_Method = 'UPI'""",

        "8. Average customer rating per vehicle type": """
SELECT Vehicle_Type,
       ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY Avg_Customer_Rating DESC""",

        "9. Total booking value of successful rides": """
SELECT SUM(Booking_Value) AS Total_Success_Booking_Value
FROM ola_rides
WHERE Booking_Status = 'Success'""",

        "10. All incomplete rides with the reason": """
SELECT Booking_ID,
       Customer_ID,
       Vehicle_Type,
       Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes'""",
    }

    tab_questions, tab_search = st.tabs(
        ["📋 10 SQL Questions", "🔍 Search Rides"]
    )

    # ---------------- TAB 1: THE 10 QUESTIONS ----------------

    with tab_questions:

        question = st.selectbox(
            "Choose a question",
            list(SQL_QUESTIONS.keys())
        )

        sql = SQL_QUESTIONS[question].strip()

        st.markdown("**SQL query**")

        st.code(sql, language="sql")

        try:

            row_count = int(
                run_query(
                    engine,
                    f"SELECT COUNT(*) AS n FROM ({sql}) AS q"
                )["n"].iloc[0]
            )

            if row_count > 100:

                result = run_query(engine, sql + " LIMIT 100")

                st.caption(
                    f"{row_count:,} rows returned. "
                    "Showing the first 100."
                )

            else:

                result = run_query(engine, sql)

            st.markdown("**Result**")

            if result.shape == (1, 1):

                st.metric(
                    result.columns[0].replace("_", " "),
                    f"{result.iloc[0, 0]:,}"
                )

            else:

                st.dataframe(
                    result,
                    use_container_width=True
                )

        except Exception as e:

            st.error(f"Query failed: {e}")

    # ---------------- TAB 2: SEARCH ----------------

    with tab_search:

        st.markdown(
            "Search by Booking ID, Customer ID, "
            "pickup location or drop location."
        )

        search_text = st.text_input(
            "Search",
            placeholder="e.g. CNR2940424040, CID225428 or Varthur"
        )

        search_col1, search_col2 = st.columns(2)

        status_choice = search_col1.selectbox(
            "Booking status",
            ["All"] + sorted(df["Booking_Status"].dropna().unique())
        )

        vehicle_choice = search_col2.selectbox(
            "Vehicle type",
            ["All"] + sorted(df["Vehicle_Type"].dropna().unique())
        )

        if not search_text.strip():

            st.info("Type something above to search the rides.")

        else:

            conditions = [
                "(Booking_ID LIKE :q OR Customer_ID LIKE :q "
                "OR Pickup_Location LIKE :q OR Drop_Location LIKE :q)"
            ]

            params = {"q": f"%{search_text.strip()}%"}

            if status_choice != "All":
                conditions.append("Booking_Status = :status")
                params["status"] = status_choice

            if vehicle_choice != "All":
                conditions.append("Vehicle_Type = :vehicle")
                params["vehicle"] = vehicle_choice

            where_clause = " AND ".join(conditions)

            try:

                found = int(
                    run_query(
                        engine,
                        f"SELECT COUNT(*) AS n FROM ola_rides WHERE {where_clause}",
                        params
                    )["n"].iloc[0]
                )

                if found == 0:

                    st.warning("No rides match your search.")

                else:

                    results = run_query(
                        engine,
                        "SELECT Booking_ID, `Date`, Customer_ID, Booking_Status, "
                        "Vehicle_Type, Pickup_Location, Drop_Location, "
                        "Booking_Value, Payment_Method, Ride_Distance "
                        f"FROM ola_rides WHERE {where_clause} "
                        "ORDER BY `Date` DESC LIMIT 500",
                        params
                    )

                    st.caption(
                        f"{found:,} rides found. Showing up to 500."
                    )

                    st.dataframe(
                        results,
                        use_container_width=True
                    )

            except Exception as e:

                st.error(f"Search failed: {e}")


# ============================================================
# PAGE 7: POWER BI DASHBOARD
# ============================================================

elif page == "Power BI":

    st.title("📈 Power BI Dashboard")

    powerbi_url = ""

    try:
        powerbi_url = st.secrets.get("powerbi_url", "")
    except Exception:
        powerbi_url = ""

    if not powerbi_url:

        powerbi_url = st.text_input(
            "Paste your Power BI 'Publish to web' link here"
        ).strip()

    if powerbi_url.startswith("https://"):

        components.iframe(
            powerbi_url,
            height=720,
            scrolling=True
        )

    elif powerbi_url:

        st.error("The link must start with https://")

    else:

        st.info(
            "The Power BI dashboard is not linked yet. "
            "Publish your report from Power BI, copy the "
            "'Publish to web' link, and paste it above. "
            "Later you can save it as powerbi_url in "
            ".streamlit/secrets.toml."
        )


# ============================================================
# 12. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center; color:gray;'>
    Ola Ride Insights | Data Analytics Project | July 2024
    </div>
    """,
    unsafe_allow_html=True
)