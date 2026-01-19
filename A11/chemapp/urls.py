from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("chembl/", views.chembl_lookup, name="chembl"),
    path("povray/", views.povray_render, name="povray"),
]
