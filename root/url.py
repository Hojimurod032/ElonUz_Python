from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeViewList.as_view(), name='home'),
    path('auth/login', LoginListView.as_view(), name='login'),
    path('auth/register', RegisterCreateView.as_view(), name='register'),
    path('post/detail/<int:detail_id>', DetailViewList.as_view(), name='detail'),
    path('profile', ProfileViewList.as_view(), name='profile'),
    path('logout', LogoutListView.as_view(), name='logout'),
    path("tariffs/", TariffListView.as_view(), name="tariff-list"),
    path("buy-plan/<int:plan_id>/", BuyPlanView.as_view(), name="buy-plan"),
    path('payment', PaymentView.as_view(), name='payment'),
    path('post/create', PostCreateView.as_view(), name='create-post'),
    path('post/<int:post_id>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('post/create/succes', PostSuccesView.as_view(), name='succes-post'),
    path('post/approve-post/<int:post_id>/', ApprovePostView.as_view(), name='approve-post'),
    path('post/rejected-post/<int:post_id>/', RejectedPostView.as_view(), name='rejected-post'),
    path('seller/<int:seller_id>/', SellerProfileView.as_view(), name='seller-profile'),

]
