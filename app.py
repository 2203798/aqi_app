import pickle
from flask import Flask, render_template, request

# flask object
app = Flask(__name__)
app.secret_key = "team_analytica_AQI"

# model properties
aqi_X_train = 0
aqi_y_train = 0
time_series = 0
ts_metrics = 0

############################################################################################
# Routing and Server methods
############################################################################################

# starting value
@app.route('/')
def index():
    return render_template("index.html", aqi=0,
                            aqi_equiv="N/A",
                            SARIMAX_series_data = [[0 , 0, 0], [0 , 0, 0], [0 , 0, 0]],
                            SARIMAX_metrics = ["---", "---", "---"],
                            RFR_metrics = ["---", "---", "---"],
                            feedback_type="primary",
                            feedback_message="No data yet.",
                            recommendations=[["N/A", 0, ["N/A"]]],
                            len_r=len(["N/A"]),
                            r_list=1)

# im here
@app.route('/aqi', methods=['POST', 'GET'])
def analyze():
    # User inputs
    inputs = get_air_pollutants()
    
    # Recommeder Algorithm
    final_inputs = convert_2D_array(inputs)
    recommendations = feedback_data_sort(feedback_data(inputs))
    
    #RFR model
    RFR_model = pickle.load(open('./RFR_model.pkl', 'rb'))
    predicted_aqi = int(RFR_model.predict(final_inputs))
    #RFR metrics
    RFR_metrics = pickle.load(open('./RFR_metrics.pkl', 'rb'))

    #SARIMAX metrics
    SARIMAX_metrics = pickle.load(open('./SARIMAX_metrics.pkl', 'rb'))
    #SARIMAX series data
    SARIMAX_series_data = pickle.load(open('./SARIMAX_series_data.pkl', 'rb'))
    print(SARIMAX_series_data)

    return render_template("index.html", aqi=predicted_aqi,
                            aqi_equiv=aqi_bucket(predicted_aqi),
                            # time_series=time_series,
                            # ts_metrics = ts_metrics,
                            # tree_metrics = [0,0,0],
                            SARIMAX_series_data = [SARIMAX_series_data[0], SARIMAX_series_data[1], SARIMAX_series_data[2]],
                            SARIMAX_metrics = SARIMAX_metrics,
                            RFR_metrics = RFR_metrics,
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
    return list

# Random Forest Regression Model
# def random_forest_regression_model(inputs, aqi_X_train, aqi_y_train): #note: 2D array
#     from sklearn.ensemble import RandomForestRegressor
#     RFR_model = RandomForestRegressor()
#     RFR_model.fit(aqi_X_train,aqi_y_train)
#     y_pred2 = RFR_model.predict(X_test)
#     from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
#     tree_metrics = [np.sqrt(mean_squared_error(y_pred2, y_test)), mean_absolute_error(y_pred2, y_test), r2_score(y_pred2, y_test)]
#     return [RFR_model.predict(inputs), tree_metrics]

if __name__ == '__main__':
    app.run(debug=True)