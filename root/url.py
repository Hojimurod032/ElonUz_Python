from django.urls import path

from .views import (
    HomeViewList,
    AuthViewList,
    DetailViewList,
    ProfileViewList,
)

urlpatterns = [
    path('', HomeViewList.as_view(), name='home'),
    path('auth', AuthViewList.as_view(), name='auth'),
    path('detail', DetailViewList.as_view(), name='detail'),
    path('profile', ProfileViewList.as_view(), name='profile'),
]