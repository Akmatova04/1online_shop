# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q # Издөө үчүн кошулду

# Моделдер, Себет классы жана Формалар
from .models import Category, Product, Review, Order, OrderItem
from .cart import Cart
from .forms import ReviewForm, CartAddProductForm, OrderCreateForm, SignUpForm

# --- 1. Башкы бет ---
def home_page(request):
    all_categories = Category.objects.all()
    popular_products = Product.objects.filter(is_popular=True, stock__gt=0)[:8]
    discounted_products = Product.objects.filter(discount_percent__gt=0, stock__gt=0)[:8]
    context = {'categories': all_categories, 'popular_products': popular_products, 'discounted_products': discounted_products}
    return render(request, 'store/home.html', context)

# --- 2. Категория барагы ---
def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, stock__gt=0)
    context = {'category': category, 'products': products}
    return render(request, 'store/category_products.html', context)

# --- 3. Продукт барагы ---
def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, stock__gt=0)
    reviews = product.reviews.all().order_by('-created_at')
    cart_product_form = CartAddProductForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, _("Пикир калтыруу үчүн сайтка киришиңиз керек."))
            return redirect(product.get_absolute_url())
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.warning(request, _("Сиз бул товарга мурунтан пикир калтыргансыз."))
            else:
                new_review = review_form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                messages.success(request, _("Пикириңиз үчүн рахмат!"))
                return redirect(product.get_absolute_url())
        else:
            messages.error(request, _("Пикир формасын туура толтуруңуз."))
    else:
        review_form = ReviewForm()
    context = {'product': product, 'reviews': reviews,'review_form': review_form, 'cart_product_form': cart_product_form}
    return render(request, 'store/product_detail.html', context)

# --- 4. Себетке кошуу ---
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
        messages.success(request, _('"{}" себетке кошулду.').format(product.name))
    else:
        messages.error(request, _("Товарды кошууда ката кетти. Санын туура киргизиңиз."))
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

# --- 5. Себеттен өчүрүү ---
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, _('"{}" себеттен өчүрүлдү.').format(product.name))
    return redirect('store:cart_detail')

# --- 6. Себетти көрсөтүү ---
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],'update': True})
    context = {'cart': cart}
    return render(request, 'store/cart_detail.html', context)

# --- 7. Буйрутма түзүү ---
def order_create(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, _("Буйрутма берүү үчүн алгач себетке товар кошуңуз."))
        return redirect('store:home')
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_amount = cart.get_total_price()
            try:
                order.save()
                for item in cart:
                    OrderItem.objects.create(order=order, product=item['product'], price_at_order=item['price'], quantity=item['quantity'])
                cart.clear()
                return redirect('store:order_created', order_id=order.id)
            except Exception as e:
                 messages.error(request, _("Буйрутманы сактоодо ката кетти: {}").format(e))
        else:
             messages.error(request, _("Сураныч, формадагы каталарды оңдоңуз."))
    else:
        initial_data = {}
        if request.user.is_authenticated:
             initial_data = {'first_name': request.user.first_name, 'last_name': request.user.last_name,}
        form = OrderCreateForm(initial=initial_data)
    context = {'cart': cart, 'form': form}
    return render(request, 'store/checkout.html', context)

# --- 8. Буйрутма ырастоо барагы ---
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user and order.user != request.user and not request.user.is_staff:
         messages.error(request, _("Сизде бул буйрутманы көрүүгө укук жок."))
         return redirect('store:home')
    context = {'order': order}
    return render(request, 'store/order_created.html', context)

# --- 9. Катталуу View (Класс катары) ---
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    def form_valid(self, form):
         messages.success(self.request, _("Сиз ийгиликтүү катталдыңыз! Эми кире аласыз."))
         return super().form_valid(form)
    def form_invalid(self, form):
         messages.error(self.request, _("Катталууда ката кетти. Сураныч, форманы текшериңиз."))
         return super().form_invalid(form)

# --- 10. Колдонуучу профили View ---
@login_required
def user_profile(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'user': request.user, 'orders': user_orders}
    return render(request, 'store/profile.html', context)

# --- 11. ИЗДӨӨ НАТЫЙЖАЛАРЫ VIEW (КОШУЛДУ) ---
def search_results(request):
    query = request.GET.get('q') # URL'ден q параметрин алабыз (?q=...)
    results = []
    if query:
        # Аталышында ЖЕ сүрөттөмөсүндө изделген сөз бар, кампада бар товарларды табабыз
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            stock__gt=0
        ).distinct()
        if not results:
             messages.info(request, f"'{query}' боюнча эч нерсе табылган жок.")
        # else:
             # messages.info(request, f"'{query}' боюнча издөө натыйжалары:") # Бул анча керек эмес
    else:
        # Эгер q параметри жок болсо же бош болсо
        messages.warning(request, "Издөө үчүн ачкыч сөз жазыңыз.")
        # Бош суроо-талапта башкы бетке кайтарсак болот:
        # return redirect('store:home')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'store/search_results.html', context)
# ----------------------------------------------
def about_page(request):
    """
    "Биз жөнүндө" маалымат барагын көрсөтөт.
    """
    context = {
        # 'page_title': 'Биз жөнүндө' # Кааласаңыз, барактын аталышын берсеңиз болот
    }
    # Жаңы түзүлө турган шаблонго жөнөтөбүз
    return render(request, 'store/about.html', context)