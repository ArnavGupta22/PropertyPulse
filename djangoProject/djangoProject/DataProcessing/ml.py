import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from tensorflow import keras
from tensorflow.keras import layers

# Load your data
# Assuming your data is already loaded into a DataFrame called 'data'

# Function to train the models and store them
def train_models(data):
    # Prepare features and targets for the first regression
    X_first = data[['city', 'year']]
    Y_first = data[['income', 'median_age', 'unemployment', 'truck_cost', 'geomobility']]

    # One-hot encoding for 'city'
    column_transformer_first = ColumnTransformer(
        transformers=[
            ('encoder', OneHotEncoder(drop='first', sparse_output=False), ['city'])
        ],
        remainder='passthrough'  # Keep the remaining columns (year)
    )

    # Transform and normalize the features and targets for the first regression
    X_first_transformed = column_transformer_first.fit_transform(X_first)
    scaler_X_first = MinMaxScaler()
    X_first_normalized = scaler_X_first.fit_transform(X_first_transformed)
    scaler_Y_first = MinMaxScaler()
    Y_first_normalized = scaler_Y_first.fit_transform(Y_first)

    # Reshape the input data for RNN
    X_first_normalized = np.array(X_first_normalized).reshape(X_first_normalized.shape[0], 1, X_first_normalized.shape[1])

    # Build and train the RNN model for socio-economic indicators
    model_first = keras.Sequential([
        layers.LSTM(100, activation='relu', return_sequences=True, input_shape=(X_first_normalized.shape[1], X_first_normalized.shape[2])),
        layers.LSTM(50, activation='relu'),
        layers.Dense(5)  # Output layer for 5 target variables
    ])

    model_first.compile(optimizer='adam', loss='mse')
    model_first.fit(X_first_normalized, Y_first_normalized, epochs=300, validation_split=0.2, batch_size=32)

    # Prepare the dataset for the second regression
    X_second = data[['city', 'year', 'income', 'median_age', 'unemployment', 'truck_cost', 'geomobility']]
    Y_second = data['housing_price']

    # Transform the features for the second regression
    column_transformer_second = ColumnTransformer(
        transformers=[
            ('encoder', OneHotEncoder(drop='first', sparse_output=False), ['city'])
        ],
        remainder='passthrough'  # Keep the remaining columns (year, income, etc.)
    )

    # Transform and normalize the features and target for the second regression
    X_second_transformed = column_transformer_second.fit_transform(X_second)
    scaler_X_second = MinMaxScaler()
    X_second_normalized = scaler_X_second.fit_transform(X_second_transformed)
    scaler_Y_second = MinMaxScaler()
    Y_second_normalized = scaler_Y_second.fit_transform(Y_second.values.reshape(-1, 1))

    # Reshape the input data for RNN
    X_second_normalized = np.array(X_second_normalized).reshape(X_second_normalized.shape[0], 1, X_second_normalized.shape[1])

    # Build and train the RNN model for housing price prediction
    model_second = keras.Sequential([
        layers.LSTM(100, activation='relu', return_sequences=True, input_shape=(X_second_normalized.shape[1], X_second_normalized.shape[2])),
        layers.LSTM(50, activation='relu'),
        layers.Dense(1)  # Output layer for housing price
    ])

    model_second.compile(optimizer='adam', loss='mse')
    model_second.fit(X_second_normalized, Y_second_normalized, epochs=300, validation_split=0.2, batch_size=32)

    return model_first, scaler_X_first, scaler_Y_first, column_transformer_first, model_second, scaler_X_second, scaler_Y_second, column_transformer_second

# Function to make predictions for multiple cities and years using pre-trained models
def predict_city_data(cities, years, model_first, scaler_X_first, scaler_Y_first, column_transformer_first, model_second, scaler_X_second, scaler_Y_second, column_transformer_second):
    results = []  # List to store results

    for city in cities:
        for year in years:
            print(f"\nPredicting for {city} in {year}...")

            # Prepare future data for socio-economic prediction
            future_data = pd.DataFrame({
                'city': [city],
                'year': [year]
            })

            # Transform and normalize the future data
            future_data_transformed = column_transformer_first.transform(future_data)
            future_data_transformed_normalized = scaler_X_first.transform(future_data_transformed)
            future_data_transformed_normalized = np.array(future_data_transformed_normalized).reshape(-1, 1, future_data_transformed_normalized.shape[1])

            # Make predictions for the future year
            future_predictions = model_first.predict(future_data_transformed_normalized)
            future_predictions_inverse = scaler_Y_first.inverse_transform(future_predictions)

            # Extract predicted values
            predicted_income, predicted_mean_age, predicted_unemployment, predicted_truck_price, predicted_geomobility = future_predictions_inverse[0]

            # Prepare the dataset for the second regression
            future_housing_data = pd.DataFrame({
                'city': [city],
                'year': [year],
                'income': [predicted_income],
                'median_age': [predicted_mean_age],
                'unemployment': [predicted_unemployment],
                'truck_cost': [predicted_truck_price],
                'geomobility': [predicted_geomobility]
            })

            # Transform and normalize the future housing data
            future_housing_data_transformed = column_transformer_second.transform(future_housing_data)
            future_housing_data_transformed_normalized = scaler_X_second.transform(future_housing_data_transformed)
            future_housing_data_transformed_normalized = np.array(future_housing_data_transformed_normalized).reshape(-1, 1, future_housing_data_transformed_normalized.shape[1])

            # Make predictions for housing price
            predicted_housing_price = model_second.predict(future_housing_data_transformed_normalized)
            predicted_housing_price_inverse = scaler_Y_second.inverse_transform(predicted_housing_price)

            # Store the results
            results.append({
                'city': city,
                'year': year,
                'predicted_income': predicted_income,
                'predicted_mean_age': predicted_mean_age,
                'predicted_unemployment': predicted_unemployment,
                'predicted_truck_cost': predicted_truck_price,
                'predicted_geomobility': predicted_geomobility,
                'predicted_housing_price': predicted_housing_price_inverse[0][0]
            })

    # Convert results list to DataFrame
    results_df = pd.DataFrame(results)
    return results_df

data = pd.read_csv("../data/merged_data.csv")
data = data.drop("Unnamed: 0", axis=1)
# Train models only once
model_first, scaler_X_first, scaler_Y_first, column_transformer_first, model_second, scaler_X_second, scaler_Y_second, column_transformer_second = train_models(data)

# Example usage
cities = data["city"].unique()  # List of unique cities
years = [2024, 2025, 2026]  # List of years
predictions_df = predict_city_data(cities, years, model_first, scaler_X_first, scaler_Y_first, column_transformer_first, model_second, scaler_X_second, scaler_Y_second, column_transformer_second)

predictions_df
