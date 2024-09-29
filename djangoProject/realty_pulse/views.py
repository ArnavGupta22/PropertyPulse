from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView


from .models import City, InvestmentMetrics, MigrationData
from .forms import FilterForm, CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
import pandas as pd


# HomePageView using TemplateView to show top cities based on ROI
class HomePageView(TemplateView):
    template_name = 'realty_pulse/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_cities'] = City.objects.all().order_by('-investmentmetrics__roi')[:10]
        return context


# CityListView using ListView to show filtered/sorted cities
import pandas as pd
from django.views.generic import ListView
from .forms import FilterForm

import pandas as pd

class CityListView(ListView):
    template_name = 'realty_pulse/city_list.html'
    context_object_name = 'cities'

    def get_queryset(self):
        # Load the CSV and convert to DataFrame
        data = pd.read_csv('djangoProject/data/predictions.csv')
        data1 = pd.read_csv('djangoProject/data/ROI.csv')

        data['predicted_truck_cost'] = data['predicted_truck_cost'] / 2000
        # Filter by city and year
        city = self.request.GET.get('city')
        year = self.request.GET.get('year')
        income = self.request.GET.get('income')

        if city or year or income:
            data.rename(columns={"predicted_income": "income"}, inplace=True)
            if city:
                data = data[data['city'].str.contains(city, case=False)]


            if year:
                data = data[data['year'] == int(year)]

            else:
                data = data[data['year'] == 2026]

            if income:
                data = data[data['income'] >= int(income)]

            data = data.reset_index(drop=True)
            data = data.drop("Unnamed: 0", axis=1)

            data1.rename(columns={"Unnamed: 0": "id"}, inplace=True)

            # Calculate ROI
            data2 = data1[data1["city"].isin(data["city"])]["ROI"]
            data2 = data2.reset_index(drop=True)

            data3 = data1[data1["city"].isin(data["city"])]["id"]
            data3 = data3.reset_index(drop=True)

            combined = pd.concat([data, data2, data3], axis=1)
            data = combined
            data.rename(columns={"ROI": "roi"}, inplace=True)

            # Sort by the selected field (ROI or Income)
            sort_by = self.request.GET.get('sort_by')
            if sort_by:
                data = data.sort_values(by=sort_by.strip('-'), ascending=sort_by[0] != '-')
            return data.to_dict(orient='records')
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilterForm(self.request.GET)
        return context


import pandas as pd
from django.views.generic import DetailView

import pandas as pd
from django.views.generic import DetailView


class CityDetailView(DetailView):
    template_name = 'realty_pulse/city_detail.html'
    context_object_name = 'city'

    def get_object(self):
        # Get the primary key from the URL kwargs
        pk = self.kwargs.get('pk')
        print(f"Primary key from URL: {pk}")  # Debugging

        # Load the CSVs
        data1 = pd.read_csv('djangoProject/data/ROI.csv')
        data = pd.read_csv('djangoProject/data/predictions.csv')

        # Rename the column for easy access
        data1.rename(columns={"Unnamed: 0": "id"}, inplace=True)

        # Filter ROI data to find the city by primary key
        city_row = data1[data1['id'] == int(pk)]
        print("City row found:", city_row)  # Debugging

        # Check if we found the city
        if not city_row.empty:
            city_name = city_row.iloc[0]["city"]
            print(f"City found: {city_name}")  # Debugging

            # Create a dictionary to hold city information
            city_info = {
                'city': city_name,
                'predicted_income': None,
                'predicted_unemployment': None,
                'predicted_geomobility': None,
                'roi': None
            }

            # Get the ROI
            roi = data1[data1['city'] == city_name]["ROI"].values
            city_info['roi'] = roi[0] if len(roi) > 0 else None

            # Get the corresponding row from predictions if available
            prediction_row = data[data['city'] == city_name]

            # Check if the prediction row is not empty and extract values
            if not prediction_row.empty:
                # Get the values for income, unemployment, and geomobility if they exist
                city_info['predicted_income'] = prediction_row.iloc[0].get('predicted_income', None)
                city_info['predicted_unemployment'] = prediction_row.iloc[0].get('predicted_unemployment', None)
                city_info['predicted_geomobility'] = prediction_row.iloc[0].get('predicted_geomobility', None)

            print("City info collected:", city_info)  # Debugging
            return city_info  # Return city information as a dictionary
        return None  # No city found with the given pk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        city = self.get_object()  # Call the modified get_object

        if city is not None:  # Ensure city is not None
            # Load the predictions CSV to extract time-series data for the selected city
            data = pd.read_csv('djangoProject/data/predictions.csv')

            # Filter the data for the selected city
            city_name = city['city']
            city_data = data[data['city'] == city_name]

            # Debugging: Print the filtered city_data
            print("Filtered city data:", city_data)  # Debugging

            if not city_data.empty:
                # Set ROI for all entries in city_data
                city_data['roi'] = city['roi']

                # If you want to display multiple years of data, such as time series
                context['time_series'] = city_data[['year', 'predicted_housing_price', 'predicted_truck_cost']].to_dict(
                    orient='records')

                # Use the 2026 values for display
                latest_data = city_data[city_data['year'] == 2026]
                if not latest_data.empty:
                    latest_prediction = latest_data.iloc[0]  # Get the prediction for 2026
                    context['latest_housing_price'] = latest_prediction['predicted_housing_price']
                    context['latest_truck_cost'] = latest_prediction['predicted_truck_cost']
                else:
                    context['latest_housing_price'] = None
                    context['latest_truck_cost'] = None

                # Update context with city information
                context['city'] = city  # Store city information for the template
            else:
                context['latest_housing_price'] = None
                context['latest_truck_cost'] = None
                context['error'] = "No prediction data found for this city."
        else:
            context['error'] = "City not found"

        print("Context data prepared:", context)  # Debugging
        return context


class RegisterFormView(FormView):
    template_name = 'realty_pulse/register.html'
    form_class = CustomUserCreationForm  # or RegistrationForm
    success_url = reverse_lazy('realty_pulse:login')  # Redirect to login after successful registration

    def form_valid(self, form):
        # Save the new user
        user = form.save()

        # Automatically log in the new user if you want (optional)
        login(self.request, user)

        return super().form_valid(form)

class LoginFormView(FormView):
    template_name = 'realty_pulse/login.html'
    form_class = AuthenticationForm
    success_url = '/realty_pulse/home'  # Redirect after successful login

    def form_valid(self, form):
        # Authenticate the user
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid username or password")
            return self.form_invalid(form)


