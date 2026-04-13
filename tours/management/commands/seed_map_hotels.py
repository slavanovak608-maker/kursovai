"""Заполняет координаты, визу и демо-отели для уже созданных путёвок (по названию/направлению)."""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.models import HotelOption, Tour


class Command(BaseCommand):
    help = "Карта, виза и варианты отелей для демо-путёвок"

    def handle(self, *args, **options):
        specs = [
            {
                "needle": ("Анталья", "Турция"),
                "fields": {
                    "departure_city": "Москва",
                    "visa_status": Tour.VisaStatus.NOT_NEEDED,
                    "visa_note": "Для граждан РФ при поездках до 60 дней виза не нужна (актуальные правила уточняйте перед выездом).",
                    "origin_lat": 55.7558,
                    "origin_lng": 37.6173,
                    "dest_lat": 36.8969,
                    "dest_lng": 30.7133,
                },
                "hotels": [
                    ("Отель 4* (включён в тур)", "Стандартный номер, завтраки", 4, Decimal("0"), 0),
                    ("Отель 5* премиум", "Sea view, расширенное питание", 5, Decimal("22000"), 1),
                    ("Family Suite", "Семейные апартаменты", 5, Decimal("35000"), 2),
                ],
            },
            {
                "needle": ("Хургада", "Египет"),
                "fields": {
                    "departure_city": "Москва",
                    "visa_status": Tour.VisaStatus.ON_ARRIVAL,
                    "visa_note": "Обычно оформляется виза по прилёту или e-visa; уточняйте в агентстве.",
                    "origin_lat": 55.7558,
                    "origin_lng": 37.6173,
                    "dest_lat": 27.2579,
                    "dest_lng": 33.8116,
                },
                "hotels": [
                    ("Отель 4* у кораллов", "Риф рядом, стандартный номер", 4, Decimal("0"), 0),
                    ("Бутик-отель 5*", "Меньше номеров, тихий пляж", 5, Decimal("19000"), 1),
                ],
            },
            {
                "needle": ("Сочи", "Красная"),
                "fields": {
                    "departure_city": "Москва",
                    "visa_status": Tour.VisaStatus.NOT_NEEDED,
                    "visa_note": "Внутренний перелёт или ж/д — паспорт РФ.",
                    "origin_lat": 55.7558,
                    "origin_lng": 37.6173,
                    "dest_lat": 43.6797,
                    "dest_lng": 40.2050,
                },
                "hotels": [
                    ("Апартаменты у подъёмника", "Студия, кухня", 0, Decimal("0"), 0),
                    ("Отель 4* у Розы Хутор", "Завтраки, шаттл до склонов", 4, Decimal("12000"), 1),
                ],
            },
            {
                "needle": ("Золотое кольцо",),
                "fields": {
                    "departure_city": "Москва",
                    "visa_status": Tour.VisaStatus.NOT_NEEDED,
                    "visa_note": "Поездка по России.",
                    "origin_lat": 55.7558,
                    "origin_lng": 37.6173,
                    "dest_lat": 57.6261,
                    "dest_lng": 39.8845,
                },
                "hotels": [
                    ("Гостиница 3* (групповой тур)", "Размещение с соседом по номеру", 3, Decimal("0"), 0),
                    ("Одноместное размещение", "Доплата за одноместный номер", 3, Decimal("8500"), 1),
                ],
            },
        ]

        updated = 0
        with transaction.atomic():
            for tour in Tour.objects.all():
                title_l = tour.title.lower()
                dest_l = tour.destination.lower()
                for spec in specs:
                    if all(
                        (n.lower() in title_l or n.lower() in dest_l) for n in spec["needle"]
                    ):
                        for k, v in spec["fields"].items():
                            setattr(tour, k, v)
                        tour.save()
                        for name, desc, stars, sur, order in spec["hotels"]:
                            HotelOption.objects.update_or_create(
                                tour=tour,
                                name=name,
                                defaults={
                                    "description": desc,
                                    "stars": stars,
                                    "surcharge_per_person": sur,
                                    "sort_order": order,
                                },
                            )
                        self.stdout.write(self.style.SUCCESS(f"OK: {tour.title}"))
                        updated += 1
                        break

        if not updated:
            self.stdout.write("Ни одна путёвка не подошла под шаблоны. Добавьте туры или правьте needle в команде.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Готово, обновлено путёвок: {updated}"))
