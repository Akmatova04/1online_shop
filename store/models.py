# store/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Аталышы"))
    slug = models.SlugField(max_length=110, unique=True, blank=True, verbose_name=_("URL Аты (автоматтык)"))
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name=_("Сүрөтү"))

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) if self.name else f'category-{uuid.uuid4().hex[:6]}'
            if not base_slug: base_slug = f'category-{self.id or uuid.uuid4().hex[:6]}'
            unique_slug = base_slug; num = 1; temp_slug = unique_slug
            while Category.objects.filter(slug=temp_slug).exclude(pk=self.pk).exists():
                temp_slug = f'{unique_slug}-{num}'; num += 1
            self.slug = temp_slug
        super().save(*args, **kwargs)

    def __str__(self): return self.name
    class Meta: verbose_name = _("Категория"); verbose_name_plural = _("Категориялар"); ordering = ['name']

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name=_("Категориясы"))
    name = models.CharField(max_length=200, verbose_name=_("Аталышы"))
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name=_("URL Аты (автоматтык)"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Сүрөттөмөсү"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Баасы (сом)"))
    weight_unit = models.CharField(max_length=20, default='даана', choices=[('кг','кг'),('г','г'),('л','литр'),('мл','мл'),('даана','даана')], verbose_name=_("Өлчөм бирдиги"))
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Сүрөтү"))
    discount_percent = models.IntegerField(default=0, verbose_name=_("Арзандатуу (%)"))
    is_popular = models.BooleanField(default=False, verbose_name=_("Популярдуубу?"))
    stock = models.PositiveIntegerField(default=1, verbose_name=_("Кампадагы саны"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Кошулган убактысы"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Жаңыртылган убактысы"))

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) if self.name else f'product-{uuid.uuid4().hex[:8]}'
            if not base_slug: base_slug = f'product-{self.id or uuid.uuid4().hex[:8]}'
            unique_slug = base_slug; num = 1; temp_slug = unique_slug
            while Product.objects.filter(slug=temp_slug).exclude(pk=self.pk).exists():
                temp_slug = f'{unique_slug}-{num}'; num += 1
            self.slug = temp_slug
        super().save(*args, **kwargs)

    def __str__(self): return self.name
    def get_discounted_price(self):
        if 0 < self.discount_percent <= 100: return round(self.price - (self.price * self.discount_percent / 100), 2)
        return self.price
    def get_absolute_url(self): return reverse('store:product_detail', kwargs={'product_slug': self.slug})
    class Meta: verbose_name = _("Азык"); verbose_name_plural = _("Азыктар"); ordering = ['-created_at']

class Order(models.Model):
    STATUS_CHOICES = [('pending',_('Күтүүдө')), ('processing',_('Иштелүүдө')), ('shipped',_('Жолдо')), ('delivered',_('Жеткирилди')), ('cancelled',_('Жокко чыгарылды'))]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Колдонуучу"))
    first_name = models.CharField(_("Аты"), max_length=100, blank=False)
    last_name = models.CharField(_("Фамилиясы"), max_length=100, blank=False)
    guest_phone = models.CharField(_("Байланыш телефону"), max_length=20, blank=False)
    shipping_address = models.TextField(_("Жеткирүү дареги"), blank=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Түзүлгөн убактысы"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Жаңыртылган убактысы"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name=_("Жалпы суммасы"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Абалы (статусу)"))

    def __str__(self):
        customer_info = f"{self.first_name} {self.last_name}".strip()
        if not customer_info and self.user: customer_info = self.user.username
        if not customer_info: customer_info = self.guest_phone or _("Конок")
        return f"{_('Буйрутма')} #{self.id} - {customer_info}"
    class Meta: verbose_name = _("Буйрутма"); verbose_name_plural = _("Буйрутмалар"); ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_("Буйрутма"))
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT, verbose_name=_("Азык"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Саны"))
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Сатып алуу баасы"))
    def get_total_item_price(self): return self.quantity * self.price_at_order
    def __str__(self): return f"{self.quantity} x {self.product.name}"
    class Meta: verbose_name = _("Буйрутманын курамы"); verbose_name_plural = _("Буйрутманын курамдары")

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_("Азык"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Колдонуучу"))
    rating = models.PositiveIntegerField(default=5, verbose_name=_("Баасы (1-5)"))
    comment = models.TextField(verbose_name=_("Пикир"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Жазылган убактысы"))
    def __str__(self): return f"{self.user.username} - {self.product.name} ({self.rating})"
    class Meta: verbose_name = _("Сын-пикир"); verbose_name_plural = _("Сын-пикирлер"); ordering = ['-created_at']; unique_together = ('product', 'user')