from django.urls import path

from .views import (
    HomeViewList,
    DetailViewList,
    ProfileViewList, LoginListView, RegisterCreateView,
)

urlpatterns = [
    path('', HomeViewList.as_view(), name='home'),
    path('auth/login', LoginListView.as_view(), name='login'),
    path('auth/register', RegisterCreateView.as_view(), name='register'),
    path('detail', DetailViewList.as_view(), name='detail'),
    path('profile', ProfileViewList.as_view(), name='profile'),
]
