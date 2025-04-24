# store/urls.py
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.order_create, name='order_create'),
    path('order/created/<int:order_id>/', views.order_created, name='order_created'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.user_profile, name='profile'),

    # --- ИЗДӨӨ НАТЫЙЖАЛАРЫ ҮЧҮН ЖОЛ КОШУЛДУ ---
    path('search/', views.search_results, name='search_results'),
    path('about/', views.about_page, name='about'),
    # --------------------------------------------
]