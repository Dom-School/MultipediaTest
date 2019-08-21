from django.urls import path
from .views import home_page, detail_page, random_page, sorry_page

urlpatterns = [
    path('', home_page, name="home_page"),
    path('random', random_page, name="random_page"),
    path('random/<str:word>', random_page, name="random_page"),
    path('sorry/<str:word>', sorry_page, name="sorry_page"),
    path('page/<str:slug>', detail_page, name="detail_page"),
]