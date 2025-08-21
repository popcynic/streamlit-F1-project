import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import emoji
import numpy as np

# Page config
st.set_page_config(page_title="🏎️ Formula one Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Cleaned_table_part_Two.csv")
    # Create rank column if it doesn't exist
    if 'rank' not in df.columns:
        df['rank'] = df['positionOrder']
    return df

df = load_data()

# Sidebar
st.sidebar.title("🏎️ Formula 1:🚩")

years = sorted(df['year'].unique())
countries = sorted(df['country'].dropna().unique())
circuits = sorted(df['circuit_name'].dropna().unique())
drivers = sorted(df['driver_name'].dropna().unique())
constructors = sorted(df['constructor_name'].dropna().unique())

# Year filter
year_min, year_max = st.sidebar.select_slider(
    "Select year range",
    options=years,
    value=(df['year'].min(), df['year'].max())
)

# Country filter
selected_country = st.sidebar.selectbox(
    "Filter by country",
    options=["All Countries"] + countries,
    index=0  # Default to "All Countries"
)

# Circuit filter (multi + "All Circuits")
selected_circuits = st.sidebar.multiselect(
    "🏟️ Filter by Circuit",
    options=["All Circuits"] + circuits,
    default=["All Circuits"]
)

# Apply filters
filtered_df = df[(df["year"] >= year_min) & (df["year"] <= year_max)]

if selected_country != "All Countries":
    filtered_df = filtered_df[filtered_df["country"] == selected_country]

if "All Circuits" in selected_circuits:
    # If "All Circuits" is selected, don't filter by circuit
    pass
else:
    filtered_df = filtered_df[filtered_df["circuit_name"].isin(selected_circuits)]

# Navigation
page = st.sidebar.radio(
    "📌 Navigate to:",
    ['Overview', 'Race Insight', 'Driver Performance', 'Constructor Analysis', 'Fastest Lap']
)

# ================== PAGES ==================

if page == "Overview":
    st.title("📊 F1 Data Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Data Rows", f"{filtered_df.shape[0]:,}")
    col2.metric("Years", f"{filtered_df['year'].min()} - {filtered_df['year'].max()}")
    col3.metric("Drivers", f"{filtered_df['driver_name'].nunique()}")
    col4.metric("Constructors", f"{filtered_df['constructor_name'].nunique()}")

    st.subheader("📈 Races per Year")
    races_per_year = filtered_df.groupby("year")["race_id"].nunique()
    st.line_chart(races_per_year)

    st.subheader("🏆 Top Constructors by Wins")
    top_constructors = filtered_df[filtered_df['positionOrder'] == 1].groupby('constructor_name').size().sort_values(ascending=False).head(10)
    st.bar_chart(top_constructors)

# ---------------- Race Insight ----------------
elif page == "Race Insight":
    st.title("Race Insight")

    selected_year = st.selectbox(
        "Select year",
        options=sorted(filtered_df['year'].unique())
    )

    available_races = filtered_df[filtered_df["year"] == selected_year]["race_name"].unique()
    selected_race = st.selectbox(
        "Select Race",
        options=sorted(available_races)
    )

    race_df = filtered_df[
        (filtered_df["year"] == selected_year) & 
        (filtered_df["race_name"] == selected_race)
    ].sort_values('positionOrder')

    st.subheader(f"🏁 Results - {selected_race} ({selected_year})")
    st.dataframe(race_df[['positionOrder', 'driver_name', 'constructor_name', 'grid', 'points']].rename(columns={
        'positionOrder': 'Position',
        'driver_name': 'Driver',
        'constructor_name': 'Constructor',
        'grid': 'Grid Position',
        'points': 'Points'
    }))

    st.subheader("📊 Grid vs Final Position")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=race_df, 
        x="grid", 
        y="positionOrder", 
        hue="constructor_name",
        s=100,
        ax=ax
    )
    ax.set_xlabel("Starting Grid Position")
    ax.set_ylabel("Final Position")
    ax.set_title(f"Grid vs Final Position - {selected_race} {selected_year}")
    ax.invert_yaxis()
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

# ---------------- Driver Performance ----------------
elif page == "Driver Performance":
    st.title("👨‍🏭 Driver Performance")

    selected_driver = st.selectbox(
        "Select Driver",
        options=drivers
    )

    driver_df = filtered_df[filtered_df['driver_name'] == selected_driver]

    col1, col2, col3 = st.columns(3)
    col1.metric("Races Participated", len(driver_df))
    col2.metric("Wins", len(driver_df[driver_df['positionOrder'] == 1]))
    col3.metric("Podiums", len(driver_df[driver_df['positionOrder'].isin([1, 2, 3])]))

    st.subheader("📈 Performance Over Years")
    performance_by_year = driver_df.groupby('year').agg({
        'positionOrder': 'mean',
        'points': 'sum'
    }).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(performance_by_year['year'], performance_by_year['positionOrder'], marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Position")
    ax.set_title(f"{selected_driver}'s Average Position Over Time")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("💰 Points Accumulation")
    st.line_chart(performance_by_year.set_index('year')['points'])

# ---------------- Constructor Analysis ----------------
elif page == "Constructor Analysis":
    st.title("🏭 Constructor Analysis")

    selected_constructor = st.selectbox(
        "Select Constructor",
        options=constructors
    )

    constructor_df = filtered_df[filtered_df['constructor_name'] == selected_constructor]

    col1, col2, col3 = st.columns(3)
    col1.metric("Races Participated", len(constructor_df))
    col2.metric("Wins", len(constructor_df[constructor_df['positionOrder'] == 1]))
    col3.metric("Podiums", len(constructor_df[constructor_df['positionOrder'].isin([1, 2, 3])]))

    st.subheader("📈 Performance Over Years")
    constructor_performance = constructor_df.groupby('year').agg({
        'positionOrder': 'mean',
        'points': 'sum'
    }).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    ax1.plot(constructor_performance['year'], constructor_performance['positionOrder'], marker='o', color='#FF5733')
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Average Position")
    ax1.set_title("Average Race Position")
    ax1.invert_yaxis()

    ax2.bar(constructor_performance['year'], constructor_performance['points'], color='#33FF57')
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Total Points")
    ax2.set_title("Total Points per Season")

    st.pyplot(fig)

    st.subheader("🏆 Top Drivers")
    top_drivers = constructor_df.groupby('driver_name').agg({
        'positionOrder': 'mean',
        'points': 'sum',
        'race_id': 'count'
    }).sort_values('points', ascending=False).head(5)
    st.dataframe(top_drivers.style.format({
        'positionOrder': '{:.2f}',
        'points': '{:.0f}',
        'race_id': '{:.0f}'
    }))

# ---------------- Fastest Lap ----------------
elif page == "Fastest Lap":
    st.title("⏱️ Fastest Lap Analysis")
    
    # Check if fastestLapSpeed column exists
    if 'fastestLapSpeed' not in filtered_df.columns:
        st.warning("Fastest lap speed data is not available in the dataset")
    else:
        fastest_laps = filtered_df[filtered_df['rank'] == 1].copy()
        
        # Convert to numeric, handling errors
        fastest_laps['fastestLapSpeed'] = pd.to_numeric(fastest_laps['fastestLapSpeed'], errors='coerce')
        
        if fastest_laps.empty or fastest_laps['fastestLapSpeed'].isnull().all():
            st.warning("No fastest lap speed data available for the selected filters")
        else:
            st.subheader("🚀 Top 10 Fastest Laps")
            top_speeds = fastest_laps.sort_values('fastestLapSpeed', ascending=False).head(10)
            st.dataframe(top_speeds[['year', 'race_name', 'driver_name', 'constructor_name', 'fastestLapSpeed']].rename(columns={
                'year': 'Year',
                'race_name': 'Race',
                'driver_name': 'Driver',
                'constructor_name': 'Constructor',
                'fastestLapSpeed': 'Speed (kph)'
            }))

            st.subheader("📈 Fastest Lap Speed Trend")
            speed_trend = fastest_laps.groupby('year')['fastestLapSpeed'].mean().reset_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(speed_trend['year'], speed_trend['fastestLapSpeed'], marker='o', color='#FFD700')
            ax.set_xlabel("Year")
            ax.set_ylabel("Average Fastest Lap Speed (kph)")
            ax.set_title("Evolution of Fastest Lap Speeds Over Time")
            st.pyplot(fig)

            st.subheader("🏎️ Fastest Drivers")
            fastest_drivers = fastest_laps.groupby('driver_name').agg({
                'fastestLapSpeed': 'mean',
                'rank': 'count'
            }).sort_values('fastestLapSpeed', ascending=False).head(10)

            st.dataframe(
                fastest_drivers.rename(columns={
                    'fastestLapSpeed': 'Avg Speed (kph)',
                    'rank': 'Fastest Laps Achieved'
                }).style.format({'Avg Speed (kph)': '{:.2f}'})
            )

            st.subheader("🔥 Fastest Lap Speed Distribution")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.histplot(fastest_laps['fastestLapSpeed'].dropna(), bins=20, ax=ax2)
            ax2.set_xlabel("Fastest Lap Speed (kph)")
            ax2.set_ylabel("Frequency")
            ax2.set_title("Distribution of Fastest Lap Speeds")
            st.pyplot(fig2)