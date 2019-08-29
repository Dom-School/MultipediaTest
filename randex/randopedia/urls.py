from django.urls import path
from .views import home_page, random_page, sorry_page, search_result_page

urlpatterns = [
    path('', home_page, name="home_page"),
    path('random', random_page, name="random_page"),
    path('search/<str:word>', search_result_page, name="search_result_page"),
    path('sorry/<str:word>', sorry_page, name="sorry_page")
]
