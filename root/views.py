from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView

from root.forms import RegisterForm, LoginForm


class HomeViewList(TemplateView):
    template_name = 'Home.html'


class LoginListView(FormView):
    form_class = LoginForm
    template_name = 'Auth.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Hush kelibsiz")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        for i in form.errors.values():
            messages.error(self.request, i)
        return super().form_invalid(form)


class RegisterCreateView(CreateView):
    form_class = RegisterForm
    template_name = 'Auth.html'
    success_url = reverse_lazy('login')


class DetailViewList(TemplateView):
    template_name = 'Detail.html'


class ProfileViewList(TemplateView):
    template_name = 'Profile.html'
