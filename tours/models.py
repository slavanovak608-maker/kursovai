from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tour(models.Model):
    class VisaStatus(models.TextChoices):
        NOT_NEEDED = "not_needed", "Виза не требуется (по паспорту РФ)"
        REQUIRED = "required", "Нужна виза заранее"
        ON_ARRIVAL = "on_arrival", "Виза по прилёту / e-visa"
        SCHENGEN = "schengen", "Нужен Шенген или виза ЕС"

    title = models.CharField("Название путёвки", max_length=200)
    slug = models.SlugField("Слаг", unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="tours",
        verbose_name="Категория",
    )
    short_description = models.CharField("Краткое описание", max_length=320)
    description = models.TextField("Полное описание")
    destination = models.CharField("Направление / страна", max_length=150)
    departure_city = models.CharField(
        "Город вылета",
        max_length=120,
        default="Москва",
        help_text="Откуда вылет (для карты и описания).",
    )
    visa_status = models.CharField(
        "Виза",
        max_length=20,
        choices=VisaStatus.choices,
        default=VisaStatus.NOT_NEEDED,
    )
    visa_note = models.TextField(
        "Комментарий по визе",
        blank=True,
        help_text="Дополнительно: срок действия паспорта, консульство и т.д.",
    )
    origin_lat = models.FloatField(
        "Широта точки вылета",
        null=True,
        blank=True,
        help_text="Для карты (например Москва ≈ 55.76).",
    )
    origin_lng = models.FloatField(
        "Долгота точки вылета",
        null=True,
        blank=True,
        help_text="≈ 37.62 для Москвы.",
    )
    dest_lat = models.FloatField(
        "Широта пункта назначения",
        null=True,
        blank=True,
    )
    dest_lng = models.FloatField(
        "Долгота пункта назначения",
        null=True,
        blank=True,
    )
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2)
    duration_days = models.PositiveSmallIntegerField("Длительность, дней")
    departure_date = models.DateField("Дата отправления", null=True, blank=True)
    image = models.ImageField(
        "Фото обложки",
        upload_to="tours/%Y/%m/",
        blank=True,
        null=True,
    )
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Туристическая путёвка"
        verbose_name_plural = "Туристические путевки"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:detail", kwargs={"slug": self.slug})

    def has_map_points(self):
        return (
            self.origin_lat is not None
            and self.origin_lng is not None
            and self.dest_lat is not None
            and self.dest_lng is not None
        )


class HotelOption(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="hotel_options",
        verbose_name="Путёвка",
    )
    name = models.CharField("Название отеля / размещения", max_length=200)
    description = models.CharField("Кратко", max_length=400, blank=True)
    stars = models.PositiveSmallIntegerField("Звёзд", default=3)
    surcharge_per_person = models.DecimalField(
        "Доплата за чел., ₽",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        help_text="0 — входит в базовую цену путёвки.",
    )
    sort_order = models.PositiveSmallIntegerField("Порядок в списке", default=0)

    class Meta:
        verbose_name = "Вариант отеля"
        verbose_name_plural = "Варианты отелей"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.tour.title}: {self.name}"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending", "Ожидает оплаты"
        PAID = "paid", "Оплачен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Путёвка",
    )
    hotel_option = models.ForeignKey(
        HotelOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        verbose_name="Отель",
    )
    people_count = models.PositiveSmallIntegerField("Количество человек", default=1)
    base_amount = models.DecimalField("Сумма путёвки, ₽", max_digits=14, decimal_places=2)
    hotel_surcharge_total = models.DecimalField(
        "Доплата за отели, ₽",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
    )
    total_amount = models.DecimalField("Итого к оплате, ₽", max_digits=14, decimal_places=2)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    paid_at = models.DateTimeField("Оплачен", null=True, blank=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]

    def __str__(self):
        return f"№{self.pk} — {self.tour.title} ({self.user})"
