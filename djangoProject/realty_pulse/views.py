from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView
from .models import City, InvestmentMetrics, MigrationData
from .forms import FilterForm, CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login


# HomePageView using TemplateView to show top cities based on ROI
class HomePageView(TemplateView):
    template_name = 'realty_pulse/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_cities'] = City.objects.all().order_by('-investmentmetrics__roi')[:10]
        return context


# CityListView using ListView to show filtered/sorted cities
class CityListView(ListView):
    model = City
    template_name = 'realty_pulse/city_list.html'
    context_object_name = 'cities'

    def get_queryset(self):
        queryset = City.objects.all()
        sort_by = self.request.GET.get('sort_by')

        if sort_by:
            queryset = queryset.order_by(sort_by)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilterForm(self.request.GET)
        return context


# CityDetailView using DetailView to show detailed info about a city
class CityDetailView(DetailView):
    model = City
    template_name = 'realty_pulse/city_detail.html'
    context_object_name = 'city'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = self.get_object()
        context['investment_data'] = InvestmentMetrics.objects.get(city=city)
        context['migration_data'] = MigrationData.objects.get(city=city)
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


