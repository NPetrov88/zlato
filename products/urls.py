from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('out-of-stock/', views.out_of_stock, name='out_of_stock'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('returns-policy/', views.returns_policy, name='returns_policy'),
]
