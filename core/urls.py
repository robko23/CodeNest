from django.urls import path
import core.views as views

urlpatterns = [
    path('time/', views.current_datetime),
]
