from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Category, HotelOption, Tour

admin.site.site_header = "Туристические путевки"
admin.site.site_title = "Админка"
admin.site.index_title = "Управление каталогом"


class HotelOptionInline(admin.TabularInline):
    model = HotelOption
    extra = 1
    ordering = ("sort_order", "id")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    inlines = [HotelOptionInline]
    list_display = (
        "thumb",
        "title",
        "category",
        "departure_city",
        "destination",
        "price",
        "visa_status",
        "duration_days",
        "is_published",
        "created_at",
    )
    list_filter = ("category", "is_published", "visa_status", "destination")
    search_fields = ("title", "destination", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)
    readonly_fields = ("thumb_large", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "is_published",
                    "image",
                    "thumb_large",
                )
            },
        ),
        (
            "Описание и маршрут",
            {
                "fields": (
                    "short_description",
                    "description",
                    "departure_city",
                    "destination",
                )
            },
        ),
        (
            "Виза",
            {"fields": ("visa_status", "visa_note")},
        ),
        (
            "Карта (координаты WGS84)",
            {
                "description": "Точки «откуда» и «куда» для карты на сайте. Подсказка: Яндекс/Google карты — правый клик по точке.",
                "fields": (
                    "origin_lat",
                    "origin_lng",
                    "dest_lat",
                    "dest_lng",
                ),
            },
        ),
        (
            "Условия",
            {
                "fields": (
                    "price",
                    "duration_days",
                    "departure_date",
                )
            },
        ),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Фото")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;object-fit:cover"/>',
                obj.image.url,
            )
        return "—"

    @admin.display(description="Предпросмотр")
    def thumb_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:320px;border-radius:12px;"/>',
                obj.image.url,
            )
        return "Загрузите изображение выше"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "people_count",
        "total_amount",
        "status",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "tour__title")
    readonly_fields = ("created_at", "paid_at")
    raw_id_fields = ("user", "tour", "hotel_option")
