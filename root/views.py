from django.shortcuts import render
from django.views.generic import TemplateView


class HomeViewList(TemplateView):
    template_name = 'Home.html'


class AuthViewList(TemplateView):
    template_name = 'Auth.html'


class DetailViewList(TemplateView):
    template_name = 'Detail.html'


class ProfileViewList(TemplateView):
    template_name = 'Profile.html'
