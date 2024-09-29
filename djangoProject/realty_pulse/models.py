from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    population = models.IntegerField()
    average_property_price = models.DecimalField(max_digits=10, decimal_places=2)
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2)

class InvestmentMetrics(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    roi = models.DecimalField(max_digits=5, decimal_places=2)
    rental_yield = models.DecimalField(max_digits=5, decimal_places=2)
    appreciation_rate = models.DecimalField(max_digits=5, decimal_places=2)

class MigrationData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    move_in_count = models.IntegerField()
    move_out_count = models.IntegerField()
    migration_trend = models.CharField(max_length=100)



