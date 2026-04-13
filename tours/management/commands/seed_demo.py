from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from tours.models import Category, Tour


class Command(BaseCommand):
    help = "Создаёт демо-категории и путёвки (без фото — их можно добавить в админке)."

    def handle(self, *args, **options):
        data = [
            {
                "cat": ("Морской отдых", "morskoy"),
                "tours": [
                    {
                        "title": "Турция, Анталья — всё включено",
                        "short": "Пляжный отель 5*, питание Ultra All Inclusive, перелёт из Москвы.",
                        "desc": "Неделя на побережье Средиземного моря: отель с бассейнами, анимация, SPA. "
                        "В стоимость входят перелёт, трансфер, страховка.",
                        "dest": "Турция, Анталья",
                        "price": Decimal("89900"),
                        "days": 7,
                        "dep": date(2026, 6, 15),
                    },
                    {
                        "title": "Египет, Хургада",
                        "short": "Кораллы, дайвинг-центр при отеле, комфортабельные номера.",
                        "desc": "Классический пляжный отдых на Красном море. Экскурсии в Луксор и Каир — по желанию.",
                        "dest": "Египет, Хургада",
                        "price": Decimal("72900"),
                        "days": 8,
                        "dep": date(2026, 5, 20),
                    },
                ],
            },
            {
                "cat": ("Горнолыжные курорты", "gornye"),
                "tours": [
                    {
                        "title": "Красная Поляна, Сочи",
                        "short": "Подъёмники, инфраструктура курорта Роза Хутор, проживание у склонов.",
                        "desc": "Зимний заезд на 5 дней: отель или апартаменты, ски-пасс можно докупить на месте.",
                        "dest": "Россия, Сочи",
                        "price": Decimal("45500"),
                        "days": 5,
                        "dep": date(2026, 1, 10),
                    },
                ],
            },
            {
                "cat": ("Экскурсионные туры", "ekskursii"),
                "tours": [
                    {
                        "title": "Золотое кольцо России",
                        "short": "Сергиев Посад, Переславль, Ростов, Ярославль — с гидом и проживанием.",
                        "desc": "Автобусный тур на 4 дня по древним городам с посещением монастырей и музеев.",
                        "dest": "Россия",
                        "price": Decimal("28900"),
                        "days": 4,
                        "dep": date(2026, 7, 5),
                    },
                ],
            },
        ]

        for block in data:
            cat_name, cat_slug = block["cat"]
            cat, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": cat_name},
            )
            for t in block["tours"]:
                slug = slugify(t["title"], allow_unicode=True)
                obj, created = Tour.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "title": t["title"],
                        "category": cat,
                        "short_description": t["short"],
                        "description": t["desc"],
                        "destination": t["dest"],
                        "price": t["price"],
                        "duration_days": t["days"],
                        "departure_date": t["dep"],
                        "is_published": True,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"+ {obj.title}"))
                else:
                    self.stdout.write(f"= уже есть: {obj.title}")

        self.stdout.write(self.style.SUCCESS("Готово. Загрузите фото в админке для каждой путёвки."))
