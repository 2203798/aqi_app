import re
from flask import Flask, render_template, request

# flask object
app = Flask(__name__)
app.secret_key = "team_analytica_AQI"

# app properties
aqi = 0
aqi_equiv = "N/A"
hourly_series_data = [["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00"], [10, 20, 30, 40, 35, 60, 50]]
daily_series_data = [["MON", "TUE", "WED", "THUR", "FRI", "SAT", "SUN"], [10, 20, 30, 40, 35, 60, 50]]
feedback_type = "primary"
feedback_message = "No data yet."
pollutants = [["N/A", 0]]
recommendations = ["N/A"]

# model properties
aqi_X_train = 0
aqi_y_train = 0

############################################################################################

# starting value
@app.route('/')
def index():
    return render_template("index.html", aqi=0,
                            aqi_equiv="N/A",
                            hourly_series_data=hourly_series_data,
                            daily_series_data=daily_series_data,
                            feedback_type=feedback_type,
                            feedback_message=feedback_message,
                            recommendations=[["N/A", 0, ["N/A"]]],
                            len_r=len(recommendations),
                            r_list=1)

# im here
@app.route('/aqi', methods=['POST', 'GET'])
def analyze():
    inputs = get_air_pollutants()
    recommendations = feedback_data_sort(feedback_data(inputs))
    predicted_aqi = int(random_forest_regression_model(convert_2D_array(inputs), aqi_X_train, aqi_y_train))
    return render_template("index.html", aqi=predicted_aqi,
                            aqi_equiv=aqi_bucket(predicted_aqi),
                            hourly_series_data=hourly_series_data,
                            daily_series_data=daily_series_data,
                            feedback_type=alert_type(predicted_aqi),
                            feedback_message=aqi_warning(predicted_aqi),
                            recommendations=recommendations,
                            len_r=len(recommendations),
                            r_list=5)

def convert_2D_array(arr):
    parentCell = []
    childCell = []
    for i in range(len(arr)):
        childCell.append(float(arr[i][1]))
    parentCell.append(childCell)
    return parentCell

def get_air_pollutants():
    #[name, value]
    pm25 = 0.0
    pm10 = 0.0
    nox = 0.0
    nh3 = 0.0
    o3 = 0.0
    co = 0.0
    so2 = 0.0
    if pm25 != '':
        pm25 = request.form['pm25']
    if pm10 != '':
        pm10 = request.form['pm10']
    if nox != '':
        nox = request.form['nox']
    if nh3 != '':
        nh3 = request.form['nh3']
    if o3 != '':
        o3 = request.form['o3']
    if co != '':
        co = request.form['co']
    if so2 != '':
        so2 = request.form['so2']
    return [
        ['PM2.5', pm25],
        ['PM10', pm10],
        ['NOx', nox],
        ['NH3', nh3],
        ['O3', o3],
        ['CO', co],
        ['SO2', so2]
    ]

def aqi_bucket(aqi):
    if aqi >= 0 and aqi <= 50:
        return "Good"
    elif aqi >= 51 and aqi <= 100:
        return "Fair"
    elif aqi >= 101 and aqi <= 150:
        return "Unhealthy"
    elif aqi >= 151 and aqi <= 200:
        return "Very Unhealthy"
    elif aqi >= 201 and aqi <= 300:
        return "Acutely Unhealthy"
    elif aqi >= 301 and aqi <= 500:
        return "Emergency"

def aqi_warning(aqi):
    if aqi >= 0 and aqi <= 50:
        return "Air quality is considered satisfactory, and air pollution poses little or no risk."
    elif aqi >= 51 and aqi <= 100:
        return "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution. Unusually sensitive individuals should consider limiting prolonged outdoor exertion."
    elif aqi >= 101 and aqi <= 150:
        return "Members of sensitive groups may experience health effects. The general public is not likely to be affected. Children, active adults, and people with respiratory disease such as asthma should limit prolonged outdoor exertion."
    elif aqi >= 151 and aqi <= 200:
        return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects. Children, active adults, and people with respiratory disease such as asthma should avoid prolonged outdoor exertion: Everyone else should limit prolonged outdoor exertion."
    elif aqi >= 201 and aqi <= 300:
        return "Health warnings of emergency conditions. The entire population is more likely to be affected. Children, active adults, and people with respiratory disease such as asthma should avoid outdoor exertion. Everyone else should limit outdoor exertion."
    elif aqi >= 301 and aqi <= 500:
        return "Everyone may experience more serious health effects. Everyone should avoid all outdoor exertion."

def feedback_data(pollutants):
    data = []
    for i in range(len(pollutants)):
        if float(pollutants[i][1]) > 0:
            data.append([pollutants[i][0], pollutants[i][1], exposure_prevention(pollutants[i][0])])
    return data

def exposure_prevention(pollutant):
    pm25 = [
        "Stay indoors in an area with filtered air.",
        "Avoid using an air cleaner that works by generating ozone, which will increase the pollution in your home.",
        "Avoid activities that make you breathe faster or more deeply. This is a good day for indoor activities, such as reading or watching TV.",
        "Do not smoke.",
        "Do not rely on dust masks for protection. Disposable respirators known as N-95 or P-100 respirators will help if you have to be outdoors for a period of time."
    ]
    pm10 = [
        "Reduce the usage of Household products which create particulate matter.",
        "Not to burn wood, leaves or any yard waste.",
        "Walk, cycle or use public transport or share vehicle wherever possible.",
        "Use Indoor Air purifiers to reduce particulate matter in homes and offices.",
        "Conserve energy by using solar energy, bio-gas, rainwater harvesting etc. to control pollution from particulate matter."
    ]
    nox = [
        "Buy vehicles with low NOx emissions and keep vehicles properly maintained, including tire pressure.",
        "Use energy efficient appliances.",
        "Reduce home energy consumption by turning off lights, televisions, and other appliances when not in use to reduce emissions from energy production.",
        "Insulate homes as much as possible.",
        "Set thermostats lower in the winter and higher in the summer, especially when away from home."
    ]
    nh3 = [
        "Wear chemical safety goggles.",
        "A face shield (with safety goggles) may also be necessary.",
        "Wear chemical protective clothing e.g. gloves, aprons, boots.",
        "In some operations: wear a chemical protective, full-body encapsulating suit and self-contained breathing apparatus.",
        "The most effective method for reducing ammonia emissions from manure application sites is to incorporate that manure into soil as quickly as possible. This drastically reduces volatilization losses resulting from exposure to air."
    ]
    o3 = [
        "Choose a cleaner commute - share a ride to work or use public transportation.",
        "Combine errands and reduce trips. Walk to errands when possible.",
        "Avoid excessive idling of your automobile.",
        "Refuel your car in the evening when it's cooler.",
        "Conserve electricity and set air conditioners no lower than 78 degrees."
    ]
    co = [
        "Keep gas appliances properly adjusted. Use proper fuel in kerosene space heaters. Open flues when fireplaces are in use. Install and use an exhaust fan vented outdoors over gas stoves.",
        "Choose properly sized wood stoves that are certified to meet EPA emission standards. Make certain that doors on all wood stoves fit tightly.",
        "Have a trained professional inspect, clean and tune-up the central heating system (furnaces, flues and chimneys) annually.",
        "Repair any leaks promptly.",
        "Do not idle the car inside the garage."
    ]
    so2 = [
        "Limit time spent outdoors while levels of air pollution are high.",
        "SO2 is one of many pollutants that should be avoided. Avoiding high levels of air pollution will reduce exposure to more pollutants than just SO2.",
        "Live further away from any power plants or other areas with heavy industrial processes nearby.",
        "Use safety equipment. Since workers typically breathe in the sulfur dioxide from their work environment, they do not bring it home with them. However, the workers can limit their exposure by wearing masks and other required safety equipment at work.",
        "Utilize air cleaners, such as an air purifier, within indoor spaces to help improve the quality of your indoor air."
    ]
    if pollutant == 'PM2.5':
        return pm25
    elif pollutant == 'PM10':
        return pm10
    elif pollutant == 'NOx':
        return nox
    elif pollutant == 'NH3':
        return nh3
    elif pollutant == 'O3':
        return o3
    elif pollutant == 'CO':
        return co
    elif pollutant == 'SO2':
        return so2

def alert_type(aqi):
    if aqi >= 0 and aqi <= 50:
        return 'success'
    elif aqi >= 51 and aqi <= 150:
        return 'warning'
    elif aqi >= 151:
        return 'danger'

def feedback_data_sort(list):
    for i in range(len(list)):  
        for j in range(len(list)-1):
            if(float(list[j][1])<float(list[j+1][1])):  
                temp = list[j]  
                list[j] = list[j+1]  
                list[j+1] = temp
    print(list)
    return list

# Random Forest Regression Model
def random_forest_regression_model(inputs, aqi_X_train, aqi_y_train): #note: 2D array
    from sklearn.ensemble import RandomForestRegressor
    RFR_model = RandomForestRegressor()
    RFR_model.fit(aqi_X_train,aqi_y_train)
    return RFR_model.predict(inputs)


############################################################################################

##### MODELS ######
# Data Preparation
# Importing packages
import numpy as np
import pandas as pd

PATH_STATION_HOUR = "./static/dataset/station_hour.csv"
PATH_STATION_DAY = "./static/dataset/station_day.csv"
PATH_CITY_HOUR = "./static/dataset/city_hour.csv"
PATH_CITY_DAY = "./static/dataset/city_day.csv"
PATH_STATIONS = "./static/dataset/stations.csv"

STATIONS = ["KL007", "KL008"] # Kariavattom, Thiruvananthapuram & Plammoodu, Thiruvananthapuram

# importing data and subsetting the station
df = pd.read_csv(PATH_STATION_HOUR, parse_dates = ["Datetime"])
stations = pd.read_csv(PATH_STATIONS)

df = df.merge(stations, on = "StationId")

df = df[df.StationId.isin(STATIONS)]
df.sort_values(["StationId", "Datetime"], inplace = True)
df["Date"] = df.Datetime.dt.date.astype(str)
df.Datetime = df.Datetime.astype(str)

df["PM10_24hr_avg"] = df.groupby("StationId")["PM10"].rolling(window = 24, min_periods = 16).mean().values
df["PM2.5_24hr_avg"] = df.groupby("StationId")["PM2.5"].rolling(window = 24, min_periods = 16).mean().values
df["SO2_24hr_avg"] = df.groupby("StationId")["SO2"].rolling(window = 24, min_periods = 16).mean().values
df["NOx_24hr_avg"] = df.groupby("StationId")["NOx"].rolling(window = 24, min_periods = 16).mean().values
df["NH3_24hr_avg"] = df.groupby("StationId")["NH3"].rolling(window = 24, min_periods = 16).mean().values
df["CO_8hr_max"] = df.groupby("StationId")["CO"].rolling(window = 8, min_periods = 1).max().values
df["O3_8hr_max"] = df.groupby("StationId")["O3"].rolling(window = 8, min_periods = 1).max().values

## PM2.5 Sub-Index calculation
def get_PM25_subindex(x):
    if x <= 30:
        return x * 50 / 30
    elif x <= 60:
        return 50 + (x - 30) * 50 / 30
    elif x <= 90:
        return 100 + (x - 60) * 100 / 30
    elif x <= 120:
        return 200 + (x - 90) * 100 / 30
    elif x <= 250:
        return 300 + (x - 120) * 100 / 130
    elif x > 250:
        return 400 + (x - 250) * 100 / 130
    else:
        return 0

df["PM2.5_SubIndex"] = df["PM2.5_24hr_avg"].apply(lambda x: get_PM25_subindex(x))

## PM10 Sub-Index calculation
def get_PM10_subindex(x):
    if x <= 50:
        return x
    elif x <= 100:
        return x
    elif x <= 250:
        return 100 + (x - 100) * 100 / 150
    elif x <= 350:
        return 200 + (x - 250)
    elif x <= 430:
        return 300 + (x - 350) * 100 / 80
    elif x > 430:
        return 400 + (x - 430) * 100 / 80
    else:
        return 0

df["PM10_SubIndex"] = df["PM10_24hr_avg"].apply(lambda x: get_PM10_subindex(x))

## SO2 Sub-Index calculation
def get_SO2_subindex(x):
    if x <= 40:
        return x * 50 / 40
    elif x <= 80:
        return 50 + (x - 40) * 50 / 40
    elif x <= 380:
        return 100 + (x - 80) * 100 / 300
    elif x <= 800:
        return 200 + (x - 380) * 100 / 420
    elif x <= 1600:
        return 300 + (x - 800) * 100 / 800
    elif x > 1600:
        return 400 + (x - 1600) * 100 / 800
    else:
        return 0

df["SO2_SubIndex"] = df["SO2_24hr_avg"].apply(lambda x: get_SO2_subindex(x))

## NOx Sub-Index calculation
def get_NOx_subindex(x):
    if x <= 40:
        return x * 50 / 40
    elif x <= 80:
        return 50 + (x - 40) * 50 / 40
    elif x <= 180:
        return 100 + (x - 80) * 100 / 100
    elif x <= 280:
        return 200 + (x - 180) * 100 / 100
    elif x <= 400:
        return 300 + (x - 280) * 100 / 120
    elif x > 400:
        return 400 + (x - 400) * 100 / 120
    else:
        return 0

df["NOx_SubIndex"] = df["NOx_24hr_avg"].apply(lambda x: get_NOx_subindex(x))

## NH3 Sub-Index calculation
def get_NH3_subindex(x):
    if x <= 200:
        return x * 50 / 200
    elif x <= 400:
        return 50 + (x - 200) * 50 / 200
    elif x <= 800:
        return 100 + (x - 400) * 100 / 400
    elif x <= 1200:
        return 200 + (x - 800) * 100 / 400
    elif x <= 1800:
        return 300 + (x - 1200) * 100 / 600
    elif x > 1800:
        return 400 + (x - 1800) * 100 / 600
    else:
        return 0

df["NH3_SubIndex"] = df["NH3_24hr_avg"].apply(lambda x: get_NH3_subindex(x))

## CO Sub-Index calculation
def get_CO_subindex(x):
    if x <= 1:
        return x * 50 / 1
    elif x <= 2:
        return 50 + (x - 1) * 50 / 1
    elif x <= 10:
        return 100 + (x - 2) * 100 / 8
    elif x <= 17:
        return 200 + (x - 10) * 100 / 7
    elif x <= 34:
        return 300 + (x - 17) * 100 / 17
    elif x > 34:
        return 400 + (x - 34) * 100 / 17
    else:
        return 0

df["CO_SubIndex"] = df["CO_8hr_max"].apply(lambda x: get_CO_subindex(x))

## O3 Sub-Index calculation
def get_O3_subindex(x):
    if x <= 50:
        return x * 50 / 50
    elif x <= 100:
        return 50 + (x - 50) * 50 / 50
    elif x <= 168:
        return 100 + (x - 100) * 100 / 68
    elif x <= 208:
        return 200 + (x - 168) * 100 / 40
    elif x <= 748:
        return 300 + (x - 208) * 100 / 539
    elif x > 748:
        return 400 + (x - 400) * 100 / 539
    else:
        return 0

df["O3_SubIndex"] = df["O3_8hr_max"].apply(lambda x: get_O3_subindex(x))

## AQI bucketing
def get_AQI_bucket(x):
    if x <= 50:
        return "Good"
    elif x <= 100:
        return "Satisfactory"
    elif x <= 200:
        return "Moderate"
    elif x <= 300:
        return "Poor"
    elif x <= 400:
        return "Very Poor"
    elif x > 400:
        return "Severe"
    else:
        return np.NaN

df["Checks"] = (df["PM2.5_SubIndex"] > 0).astype(int) + \
                (df["PM10_SubIndex"] > 0).astype(int) + \
                (df["SO2_SubIndex"] > 0).astype(int) + \
                (df["NOx_SubIndex"] > 0).astype(int) + \
                (df["NH3_SubIndex"] > 0).astype(int) + \
                (df["CO_SubIndex"] > 0).astype(int) + \
                (df["O3_SubIndex"] > 0).astype(int)

df["AQI_calculated"] = round(df[["PM2.5_SubIndex", "PM10_SubIndex", "SO2_SubIndex", "NOx_SubIndex",
                                 "NH3_SubIndex", "CO_SubIndex", "O3_SubIndex"]].max(axis = 1))
df.loc[df["PM2.5_SubIndex"] + df["PM10_SubIndex"] <= 0, "AQI_calculated"] = np.NaN
df.loc[df.Checks < 3, "AQI_calculated"] = np.NaN

df["AQI_bucket_calculated"] = df["AQI_calculated"].apply(lambda x: get_AQI_bucket(x))
final_df = df[~df.AQI_calculated.isna()]

df[~df.AQI_calculated.isna()].AQI_bucket_calculated.value_counts()

# Day level AQI
df_station_hour = df
df_station_day = pd.read_csv(PATH_STATION_DAY)

# City Level AQI
df_station_day = df_station_day.merge(df.groupby(["StationId", "Date"])["AQI_calculated"].mean().reset_index(), on = ["StationId", "Date"])
df_station_day.AQI_calculated = round(df_station_day.AQI_calculated)

df_city_hour = pd.read_csv(PATH_CITY_HOUR)
df_city_day = pd.read_csv(PATH_CITY_DAY)

df_city_hour["Date"] = pd.to_datetime(df_city_hour.Datetime).dt.date.astype(str)

df_city_hour = df_city_hour.merge(df.groupby(["City", "Datetime"])["AQI_calculated"].mean().reset_index(), on = ["City", "Datetime"])
df_city_hour.AQI_calculated = round(df_city_hour.AQI_calculated)

df_city_day = df_city_day.merge(df_city_hour.groupby(["City", "Date"])["AQI_calculated"].mean().reset_index(), on = ["City", "Date"])
df_city_day.AQI_calculated = round(df_city_day.AQI_calculated)

# Data Preprocessing and Cleaning
final_df = final_df.drop(['Benzene', 'Toluene', 'Xylene', 'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'AQI', 'AQI_Bucket', 'PM10_24hr_avg', 'PM2.5_24hr_avg', 'SO2_24hr_avg', 'NOx_24hr_avg', 'NH3_24hr_avg', 'CO_8hr_max', 'O3_8hr_max', 'Checks'], axis=1)
# filling missing value using fillna() 
final_df = final_df.fillna(0)

final_df['Datetime'] = pd.to_datetime(df['Datetime'], format='%y/%m/%d %H:%M:%S', infer_datetime_format=True) 
final_df['Datetime'] = final_df['Datetime'].astype('datetime64[ns]')

from sklearn.model_selection import train_test_split
y = final_df["AQI_calculated"]
x = final_df[['PM2.5_SubIndex', 'PM10_SubIndex', 'SO2_SubIndex', 'NOx_SubIndex', 'NH3_SubIndex', 'CO_SubIndex', 'O3_SubIndex']]
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)

# variable assignment (aqi training)
aqi_X_train = X_train
aqi_y_train = y_train

if __name__ == '__main__':
    app.run(debug=True)