from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, HotelOption, Tour


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта", required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "Логин",
        }


class BookingStartForm(forms.Form):
    people_count = forms.IntegerField(
        label="Количество человек",
        min_value=1,
        max_value=20,
        initial=1,
    )
    hotel_option = forms.ModelChoiceField(
        label="Отель / размещение",
        queryset=HotelOption.objects.none(),
        required=False,
        empty_label="Стандартный отель (включён в цену, без доплаты)",
    )

    def __init__(self, *args, tour: Tour | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if tour is not None:
            self.fields["hotel_option"].queryset = tour.hotel_options.all()


class MockPaymentForm(forms.Form):
    card_holder = forms.CharField(label="Имя на карте", max_length=120)
    card_number = forms.CharField(
        label="Номер карты (учебный ввод)",
        max_length=19,
        min_length=12,
        help_text="Данные не сохраняются. Для курсовой — любые цифры.",
    )

    def clean_card_number(self):
        raw = "".join(c for c in self.cleaned_data["card_number"] if c.isdigit())
        if len(raw) < 12:
            raise forms.ValidationError("Введите не менее 12 цифр.")
        return raw
