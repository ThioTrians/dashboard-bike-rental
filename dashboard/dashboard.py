import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from matplotlib import ticker
sns.set_theme(style='dark')

def rental_per_weather(df):
    #Membuat pivot table untuk melihat jumlah rental per-cuacanya
    weather_bike_df = df.groupby(by="weathersit").agg({
        "casual": "sum",        #ambil total peminjaman casual
        "registered": "sum",    #ambil total peminjaman registered
        "cnt": "sum"            #total peminjaman casual + registered
        }
    )
    weather_bike_df.rename_axis("weather_conditions",inplace=True)
    weather_bike_df.rename(columns={"cnt": "total_rental"}, inplace=True)

    return weather_bike_df

def rental_per_workday(df):
    #Mencari jumlah 
    workday_bike_df = df.groupby("workingday").agg({
        "casual": "sum",        #ambil total peminjaman casual
        "registered": "sum",    #ambil total peminjaman registered
        "cnt": "sum"            #total peminjaman casual + registered
        }
    )
    workday_bike_df.rename_axis("working_day",inplace=True)
    workday_bike_df.rename(columns={"cnt": "total_rental"}, inplace=True)

    return workday_bike_df

def rental_per_season(df):
    #melihat jumlah peminjaman per-musimnya
    season_sum_df = df.groupby("season").agg({
        "casual": "sum",        #ambil total peminjaman casual
        "registered": "sum",    #ambil total peminjaman registered
        "cnt": "sum"            #total peminjaman casual + registered
        }
    ).sort_values(by="cnt",ascending=False)
    season_sum_df.rename(columns={"cnt": "total_rental"}, inplace=True)


    #musim manakah yang memiliki jumlah peminjaman terbanyak dan tersedikit? (1:spring, 2:summer, 3:fall, 4:winter)
    # Max: 3 - Fall
    # Min: 1 - Spring
    return season_sum_df

def rental_per_month(df):
#Melihat jumlah peminjaman per bulan
    monthly_rental_df = df.resample(rule='ME', on='dteday').agg({
        "casual": "sum",        #ambil total peminjaman casual
        "registered": "sum",    #ambil total peminjaman registered
        "cnt": "sum"            #total peminjaman casual + registered
        }
    )

    #Merubah bentuk data dari YYYY-MM-DD menjadi YYYY-MM untuk mempermudah melihat data
    monthly_rental_df.index = monthly_rental_df.index.strftime("%Y-%m")
    monthly_rental_df = monthly_rental_df.reset_index()

    #merubah nama kolom menyesuaikan konteks
    monthly_rental_df.rename(columns={"dteday": "month", "cnt": "total_rental"}, inplace=True)
    return monthly_rental_df

#load dataframe
bike_rental_df = pd.read_csv("day.csv")

#Mengubah datatype "dteday" menjadi datetime
bike_rental_df["dteday"] = pd.to_datetime(bike_rental_df["dteday"])

#filter widget date
min_date = bike_rental_df["dteday"].min()
max_date = bike_rental_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = bike_rental_df[(bike_rental_df["dteday"] >= str(start_date)) & (bike_rental_df["dteday"] <= str(end_date))]

#Call helper functions
rental_per_weather_df = rental_per_weather(main_df)
rental_per_workday_df = rental_per_workday(main_df)
rental_per_season_df  = rental_per_season(main_df)
rental_per_month_df = rental_per_month(main_df)

#Header
st.header('Dicoding Collection Dashboard :sparkles:')

#Menampilkan daily orders
st.subheader('Daily Rentals')

col1,col2,col3 = st.columns(3)
 
with col1:
    casual_rentals = rental_per_month_df.casual.sum()
    st.metric("Casual Rentals", value=casual_rentals)

with col2:
    registered_rentals = rental_per_month_df.registered.sum()
    st.metric("Registered Rentals", value=registered_rentals)

with col3:
    total_rentals = rental_per_month_df.total_rental.sum()
    st.metric("Total Rentals (Casual + Registered)", value=total_rentals)
    

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    rental_per_month_df["month"],
    rental_per_month_df["total_rental"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=18)
 
st.pyplot(fig)

#visualisasi rental per weather condition
st.subheader("Rental Count per Weather Conditions")
#Reset dataframe index
weather_bike = rental_per_weather_df.reset_index()
#Reshape the DataFrame to a long format using pd.melt()
weather_bike_melted = pd.melt(weather_bike, id_vars="weather_conditions", 
                    value_vars=["casual", "registered", "total_rental"],
                    var_name="rental_type", value_name="count")

# Create the grouped bar chart
fig1 = plt.figure(figsize=(10, 6))
ax = sns.barplot(x='weather_conditions', y='count', hue='rental_type', palette="inferno", data=weather_bike_melted)
plt.xlabel('[Weather Conditions]\n 1: Clear, Few clouds, Partly cloudy, Partly cloudy\n 2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist\n 3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds')
plt.ylabel('[Number of Bike Rentals]')
plt.title('Number of Bike Rental by Weather Conditions')

# Merubah tampilan angka pada sumbu Y
formatter = ticker.ScalarFormatter()
formatter.set_scientific(False)
ax.yaxis.set_major_formatter(formatter)

#Memberikan nilai pada setiap bar nya untuk memperjelas jumlah rental
for container in ax.containers:
    ax.bar_label(container, labels=[f'{int(val):,}' for val in container.datavalues])

st.pyplot(fig1)

#visualisasi rental per season
st.subheader("Rental Count per Season")
#reset dataframe index
season_sum = rental_per_season_df.reset_index()
season_sum_melted = pd.melt(season_sum, id_vars="season", 
                    value_vars=["casual", "registered", "total_rental"],
                    var_name="rental_type", value_name="count")

# Create the grouped bar chart
fig3 = plt.figure(figsize=(10, 6))
ax = sns.barplot(x='season', y='count', hue='rental_type', palette="inferno", data=season_sum_melted)
plt.xlabel('[Season]\n 1: Spring\n 2:Summer\n 3:Fall\n 4:Winter')
plt.ylabel('[Number of Bike Rentals]')
plt.title('Number of Bike Rental by Seasons')

# Merubah tampilan angka pada sumbu Y
formatter = ticker.ScalarFormatter()
formatter.set_scientific(False)
ax.yaxis.set_major_formatter(formatter)

#Memberikan nilai pada setiap bar nya untuk memperjelas jumlah rental
for container in ax.containers:
    ax.bar_label(container, labels=[f'{int(val):,}' for val in container.datavalues])

st.pyplot(fig3)

#visualisasi rental per workday
st.subheader("Rental Count per Work Day")

#reset dataframe index
workday_bike = rental_per_workday_df.reset_index()
workday_bike_melted = pd.melt(workday_bike, id_vars="working_day", 
                    value_vars=["casual", "registered", "total_rental"],
                    var_name="rental_type", value_name="count")

# Create the grouped bar chart
fig2 = plt.figure(figsize=(10, 6))
ax = sns.barplot(x='working_day', y='count', hue='rental_type', palette="inferno", data=workday_bike_melted)
plt.xlabel('[Working Day]\n 0 - Libur\n 1 - working day')
plt.ylabel('[Number of Bike Rentals]')
plt.title('Number of Bike Rental by Working Day')

# Merubah tampilan angka pada sumbu Y
formatter = ticker.ScalarFormatter()
formatter.set_scientific(False)
ax.yaxis.set_major_formatter(formatter)

#Memberikan nilai pada setiap bar nya untuk memperjelas jumlah rental
for container in ax.containers:
    ax.bar_label(container, labels=[f'{int(val):,}' for val in container.datavalues])

st.pyplot(fig2)

st.caption('Copyright (c) Dicoding 2023')