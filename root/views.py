from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView

from root.forms import RegisterForm, LoginForm, CreatePostForm
from root.models import Category, PostImage, Post, Plan, User


class HomeViewList(TemplateView):
    template_name = 'Home.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        data['posts'] = Post.objects.filter(status=Post.Status.ACTIVE)

        return data


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


class LogoutListView(TemplateView):
    def post(self, request):
        logout(request)
        return redirect('home')


class RegisterCreateView(CreateView):
    form_class = RegisterForm
    template_name = 'Auth.html'
    success_url = reverse_lazy('login')


class DetailViewList(DetailView):
    queryset = Post.objects.all()
    template_name = 'Detail.html'
    pk_url_kwarg = 'detail_id'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.get_object()

        data['similar_posts'] = Post.objects.filter(
            category=post.category,
            status=Post.Status.ACTIVE
        ).exclude(id=post.id)[:4]

        post.views_count += 1
        post.save(update_fields=['views_count'])

        return data


class ProfileViewList(LoginRequiredMixin, TemplateView):
    template_name = 'Profile.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        data['posts'] = Post.objects.filter(user=self.request.user)
        data['pending_posts'] = Post.objects.filter(status=Post.Status.PENDING)
        data['post_count'] = Post.objects.filter(user=self.request.user).count()
        user_posts = Post.objects.filter(user=self.request.user)
        data['post_view_count'] = user_posts.aggregate(total_views=Sum('views_count'))['total_views']

        return data


class PaymentView(TemplateView):
    template_name = 'Payment.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = CreatePostForm
    template_name = 'Profile.html'
    success_url = reverse_lazy('succes-post')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            plan = request.user.active_plan

            today_count = Post.objects.filter(
                user=request.user,
                created_at__date=timezone.now().date()
            ).count()

            if today_count >= plan.daily_limit:
                messages.error(request, f"Kunlik limit ({plan.daily_limit} ta) tugagan. Tarifni yangilang.")
                return redirect('profile')

            total_count = Post.objects.filter(user=request.user).exclude(status=Post.Status.REJECTED).count()

            if total_count >= plan.total_limit:
                messages.error(request, f"Jami e'lon limiti ({plan.total_limit} ta) tugagan. Tarifni yangilang.")
                return redirect('profile')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(user=self.request.user)
        context['categories'] = Category.objects.all()
        if self.request.user.role == 'admin':
            context['pending_posts'] = Post.objects.filter(status=Post.Status.PENDING)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user

        if self.request.POST.get('latitude'):
            self.object.latitude = self.request.POST.get('latitude')
        if self.request.POST.get('longitude'):
            self.object.longitude = self.request.POST.get('longitude')

        if self.request.user.active_plan.code == Plan.Code.PREMIUM:
            self.object.is_premium = True

        self.object.save()

        upload_images = self.request.FILES.getlist('images')
        for idx, image in enumerate(upload_images):
            PostImage.objects.create(post=self.object, image=image, order=idx)

        messages.success(self.request, "E'loningiz muvaffaqiyatli joylandi!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ma'lumotlarni to'g'ri kiritganingizga ishonch hosil qiling.")
        return super().form_invalid(form)


class PostSuccesView(LoginRequiredMixin, TemplateView):
    template_name = 'SuccesPost.html'


class TariffListView(ListView):
    model = Plan
    template_name = "Tarifftypes.html"  # HTML faylingiz nomi
    context_object_name = "plans"
    ordering = ["price"]


class DeletePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        messages.success(request, "E'lon o'chirildi.")
        return redirect('profile')


class BuyPlanView(LoginRequiredMixin, View):

    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        user = request.user

        if user.active_plan.code == plan.code:
            messages.warning(request, "Ushbu tarif sizda allaqachon faol!")
            return redirect("tariff-list")

        if user.balance < plan.price:
            messages.error(
                request,
                f"Balansingizda mablag' yetarli emas! Sizga yana {int(plan.price - user.balance)} so'm kerak.",
            )
            return redirect("tariff-list")

        with transaction.atomic():
            user.balance -= plan.price
            user.plan = plan

            if plan.price == 0:
                user.plan_expires_at = None
            else:
                user.plan_expires_at = timezone.now() + timedelta(days=30)

            user.save()

        messages.success(
            request,
            f"Tabriklaymiz! '{plan.name}' tarifi 30 kun muddatga muvaffaqiyatli faollashtirildi.",
        )
        return redirect("profile")


class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "admin"

    def handle_no_permission(self):
        messages.error(self.request, "Sizda bu amalni bajarish uchun ruxsat yo'q.")
        return redirect('profile')


class ApprovePostView(AdminOnlyMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.ACTIVE
        post.reviewed_by = request.user
        post.save()
        messages.success(request, f'"{post.title}" e\'loni tasdiqlandi.')
        return redirect('profile')


class RejectedPostView(AdminOnlyMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.REJECTED
        post.reject_reason = request.POST.get('reject_reason', '')
        post.reviewed_by = request.user
        post.save()
        messages.success(request, f'"{post.title}" e\'loni rad etildi.')
        return redirect('profile')


class SellerProfileView(DetailView):
    model = User
    template_name = 'SellerProfile.html'
    pk_url_kwarg = 'seller_id'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.get_object()

        seller_posts = Post.objects.filter(
            user=seller,
            status=Post.Status.ACTIVE
        ).prefetch_related('images')

        context['seller_posts'] = seller_posts
        context['posts_count'] = seller_posts.count()
        total_views = seller_posts.aggregate(total=Sum('views_count'))['total'] or 0
        context['total_views'] = total_views

        return context
