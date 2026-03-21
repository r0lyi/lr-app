"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from config.error_views import page_not_found_view

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("auth:login")

urlpatterns = [
    path("", root_redirect, name="root"),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.users.urls', namespace='auth')),
    path('employees/', include('apps.employees.urls', namespace='employees')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('vacations/', include('apps.vacations.urls', namespace='vacations')),
    path("<path:unknown_path>", page_not_found_view, name="not-found"),
]
