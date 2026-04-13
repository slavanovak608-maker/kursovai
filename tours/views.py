from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingStartForm, MockPaymentForm, RegisterForm
from .models import Booking, Category, Tour


def home(request):
    featured = Tour.objects.filter(is_published=True).select_related("category")[:6]
    categories = Category.objects.all()[:8]
    return render(
        request,
        "tours/home.html",
        {"featured_tours": featured, "categories": categories},
    )


def tour_list(request):
    tours = Tour.objects.filter(is_published=True).select_related("category")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip()
    if q:
        tours = tours.filter(
            Q(title__icontains=q)
            | Q(destination__icontains=q)
            | Q(short_description__icontains=q)
        )
    if cat:
        tours = tours.filter(category__slug=cat)
    categories = Category.objects.all()
    return render(
        request,
        "tours/tour_list.html",
        {
            "tours": tours,
            "categories": categories,
            "current_category": cat,
            "search_query": q,
        },
    )


def tour_detail(request, slug):
    tour = get_object_or_404(
        Tour.objects.select_related("category").prefetch_related("hotel_options"),
        slug=slug,
        is_published=True,
    )
    similar = (
        Tour.objects.filter(is_published=True, category=tour.category)
        .exclude(pk=tour.pk)
        .select_related("category")[:3]
    )
    map_payload = None
    if tour.has_map_points():
        map_payload = {
            "oLat": float(tour.origin_lat),
            "oLng": float(tour.origin_lng),
            "dLat": float(tour.dest_lat),
            "dLng": float(tour.dest_lng),
            "originLabel": tour.departure_city,
            "destLabel": tour.destination,
        }
    return render(
        request,
        "tours/tour_detail.html",
        {"tour": tour, "similar_tours": similar, "map_payload": map_payload},
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("tours:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно. Можете бронировать путёвки.")
            return redirect("tours:home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class SiteLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class SiteLogoutView(LogoutView):
    next_page = "/"


@login_required
def tour_book(request, slug):
    tour = get_object_or_404(
        Tour.objects.prefetch_related("hotel_options"),
        slug=slug,
        is_published=True,
    )
    if request.method == "POST":
        form = BookingStartForm(request.POST, tour=tour)
        if form.is_valid():
            people = form.cleaned_data["people_count"]
            hotel = form.cleaned_data.get("hotel_option")
            if hotel and hotel.tour_id != tour.id:
                messages.error(request, "Неверный вариант отеля.")
                return redirect("tours:detail", slug=slug)
            base = tour.price * Decimal(people)
            per_hotel = (
                hotel.surcharge_per_person * Decimal(people)
                if hotel
                else Decimal("0")
            )
            total = base + per_hotel
            booking = Booking.objects.create(
                user=request.user,
                tour=tour,
                hotel_option=hotel,
                people_count=people,
                base_amount=base,
                hotel_surcharge_total=per_hotel,
                total_amount=total,
                status=Booking.Status.PENDING_PAYMENT,
            )
            return redirect("tours:pay", pk=booking.pk)
    else:
        form = BookingStartForm(tour=tour)
    return render(
        request,
        "tours/book_tour.html",
        {"tour": tour, "form": form},
    )


@login_required
def booking_pay(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related("tour", "hotel_option"),
        pk=pk,
        user=request.user,
    )
    if booking.status != Booking.Status.PENDING_PAYMENT:
        messages.info(request, "Этот заказ уже обработан.")
        return redirect("tours:my_bookings")
    if request.method == "POST":
        form = MockPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                b = Booking.objects.select_for_update().get(pk=booking.pk, user=request.user)
                if b.status != Booking.Status.PENDING_PAYMENT:
                    return redirect("tours:my_bookings")
                b.status = Booking.Status.PAID
                b.paid_at = timezone.now()
                b.save(update_fields=["status", "paid_at"])
            messages.success(
                request,
                "Оплата прошла успешно (учебный режим). Бронирование сохранено в «Мои заказы».",
            )
            return redirect("tours:my_bookings")
    else:
        form = MockPaymentForm()
    return render(
        request,
        "tours/pay_booking.html",
        {"booking": booking, "form": form},
    )


@login_required
def my_bookings(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("tour", "hotel_option")
        .order_by("-created_at")
    )
    return render(request, "tours/my_bookings.html", {"bookings": bookings})
