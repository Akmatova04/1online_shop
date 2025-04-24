# store/forms.py
from django import forms
from .models import Review, Order
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# --- 1. ПИКИР КАЛТЫРУУ ФОРМАСЫ ---
class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'type': 'number', 'step': '1', 'class': 'form-control mb-2'}), label=_("Сиздин бааңыз (1ден 5ке чейин)"))
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control mb-2'}), label=_("Сиздин пикириңиз"))
    class Meta: model = Review; fields = ['rating', 'comment']

# --- 2. СЕБЕТКЕ КОШУУ ФОРМАСЫ ---
class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control quantity-input', 'style': 'width: 60px; text-align: center; display: inline-block; margin-right: 10px;'}), label="")
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# --- 3. БУЙРУТМА БЕРҮҮ ФОРМАСЫ ---
class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(label=_('Атыңыз'), max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control mb-2'}))
    last_name = forms.CharField(label=_('Фамилияңыз'), max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control mb-2'}))
    guest_phone = forms.CharField(label=_("Байланыш телефону"), max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': '+996 XXX XXX XXX', 'class': 'form-control mb-2'}))
    shipping_address = forms.CharField(label=_("Толук жеткирүү дареги"), widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _('Шаар, көчө, үй, батир'), 'class': 'form-control mb-2'}), required=True)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'guest_phone', 'shipping_address']

# --- 4. КАТТАЛУУ ФОРМАСЫ ---
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text=_('Милдеттүү. Жарактуу email дарегин киргизиңиз.'))
    first_name = forms.CharField(max_length=30, required=False, label=_('Атыңыз'))
    last_name = forms.CharField(max_length=150, required=False, label=_('Фамилияңыз'))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email') + UserCreationForm.Meta.fields
        labels = {
            'password2': _('Сыр сөздү ырастоо'),
        }
        help_texts = {
            'password2': _('Текшерүү үчүн мурунку сыр сөздү кайра киргизиңиз.'),
        }