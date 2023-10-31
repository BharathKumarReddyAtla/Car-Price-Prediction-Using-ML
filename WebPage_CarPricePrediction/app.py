import pickle
import pandas as pd
from flask import Flask, request, render_template
from flask_mysqldb import MySQL

# Load bagging model from pickle file
with open('bagging_estimator_model1.pkl', 'rb') as f:
    bagging_dict = pickle.load(f)
    bagging_model = bagging_dict['model']

# Load label encoders from pickle file
with open('label_encoders1.pkl', 'rb') as f:
    label_encoder_objects = pickle.load(f)

# Create a Flask app
app = Flask(__name__, template_folder='D:\VS codes\Project_CarPrice')

# Configure MySQL database connection settings
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'Bharath@#123'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'car'  # Replace with your MySQL database name

# Create MySQL object
mysql = MySQL(app)

# Define home page
@app.route('/')
def home():
    return render_template('home.html')

# Define predict page
@app.route('/predict', methods=['POST'])
def predict():
    # Get input data from form
    make = request.form.get('make')
    model = request.form.get('model')
    year = int(request.form.get('year'))
    engine_fuel_type = request.form.get('engine_fuel_type')
    engine_hp = int(request.form.get('engine_hp'))
    engine_cylinders = int(request.form.get('engine_cylinders'))
    transmission_type = request.form.get('transmission_type')
    driven_wheels = request.form.get('driven_wheels')
    number_of_doors = int(request.form.get('number_of_doors'))
    market_category = request.form.get('market_category')
    vehicle_size = request.form.get('vehicle_size')
    vehicle_style = request.form.get('vehicle_style')
    highway_mpg = int(request.form.get('highway_mpg'))
    city_mpg = int(request.form.get('city_mpg'))
    popularity = int(request.form.get('popularity'))

    # Create a dataframe with input values
    input_data = pd.DataFrame({'make': [make],
                               'model': [model],
                               'year': [year],
                               'engine_fuel_type': [engine_fuel_type],
                               'engine_hp': [engine_hp],
                               'engine_cylinders': [engine_cylinders],
                               'transmission_type': [transmission_type],
                               'driven_wheels': [driven_wheels],
                               'number_of_doors': [number_of_doors],
                               'market_category': [market_category],
                               'vehicle_size': [vehicle_size],
                               'vehicle_style': [vehicle_style],
                               'highway_mpg': [highway_mpg],
                               'city_mpg': [city_mpg],
                               'popularity': [popularity]})

    # Label encode categorical columns
    cat_cols = ['make', 'model', 'engine_fuel_type', 'transmission_type', 'driven_wheels', 'market_category', 'vehicle_size', 'vehicle_style']
    label_encoder_dict = dict(zip(cat_cols, label_encoder_objects))
    for col in cat_cols:
        input_data[col] = input_data[col].astype(object)
        le = label_encoder_dict[col]
        input_data[col] = le.transform(input_data[col])

    # Make prediction using bagging model
    msrp = bagging_model.predict(input_data)
    msrp_value = str(msrp.item())  # Convert the value to string


    # Store form data in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO car_data (make, model, year, engine_fuel_type, engine_hp, engine_cylinders, transmission_type, driven_wheels, number_of_doors, market_category, vehicle_size, vehicle_style, highway_mpg, city_mpg, popularity, msrp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (make, model, year, engine_fuel_type, engine_hp, engine_cylinders, transmission_type, driven_wheels, number_of_doors, market_category, vehicle_size, vehicle_style, highway_mpg, city_mpg, popularity, msrp_value))
    mysql.connection.commit()

    # Return predicted MSRP in a template
    return render_template('result.html', msrp=msrp)

if __name__ == '__main__':
    app.run()
