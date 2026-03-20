from django.urls import path
from apps.dashboard.views.prueba import home_view

app_name = "dashboard"

urlpatterns = [
    path("", home_view, name="home"),
]
