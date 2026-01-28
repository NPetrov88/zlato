from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('apply-discount/', views.apply_discount_code, name='apply_discount'),
    path('remove-discount/', views.remove_discount_code, name='remove_discount'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/<str:order_number>/', views.order_success, name='success'),
    path('track/', views.track_order, name='track'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
