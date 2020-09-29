from django.urls import path

from django.contrib.auth import views as auth_views

from . import views
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    UserCreateView, LoginViewwe, CategoryFilter, booking, LocalPayment, AddressAdd
)

app_name = 'core'



urlpatterns = [
    path('login', LoginViewwe.as_view(), name='login'),
    path('cat/<str:cat>', CategoryFilter, name='CAT'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('signup', UserCreateView.as_view(), name='signup'),
    path('', HomeView.as_view(), name='home'),
    #path('', homepageqq, name='home2'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),

    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('LocalPayment/<int:pk>', views.LocalPayment, name='LocalPayment'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('item_list', views.articolo_alternative, name='articolo-alternative'),
    path('booking', booking, name='booking'),
    path('profile', views.ProfileView, name='profile'),
    path('contatti', views.contatti, name='contatti'),
    path('gallery', views.gallery, name='gallery'),
    path('delete/<int:pk>/delete', views.BookingDelete.as_view(), name='delete'),
    path('modificaPassword', views.PasswordChangeView, name='modica-password'),
    path('add',AddressAdd,name='address-add'),
]
