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
    UserCreateView, LoginViewwe, CategoryFilter, booking, LocalPayment, AddressAdd, address_detail, add_review
)

app_name = 'core'



urlpatterns = [
    path('login', LoginViewwe.as_view(), name='login'),
    path('cat/<str:cat>', CategoryFilter, name='CAT'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('signup', UserCreateView.as_view(), name='signup'),
    path('', HomeView.as_view(), name='home'),
    path('home2/', views.homepageqq, name='home2'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),

    path('add-review/<slug>/', add_review, name='add-review'),

    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('LocalPayment', views.LocalPayment, name='LocalPayment'),
    path('CPayment', views.Cpayment, name='CPayment'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('item_list', views.articolo_alternative, name='articolo-alternative'),
    path('booking', booking, name='booking'),
    path('profile', views.ProfileView, name='profile'),
    path('contatti', views.contatti, name='contatti'),
    path('gallery', views.gallery, name='gallery'),
    path('deleteAdress/<int:pk>/delete', views.AdressDelete.as_view(), name='Adressdelete'),
    path('delete/<int:pk>/delete', views.BookingDelete.as_view(), name='delete'),
    path(r'^password/$', views.PasswordChangeView,name='modica-password'),

    path('add',views.AddressAdd,name='address-add'),
    path('address/<int:pk>/change', views.AddressChange.as_view(), name='address-change'),
    path('address/list', views.AddressList.as_view(), name='address-list'),
    path('address/<int:pk>/detail',views.address_detail,name='address-detail'),

#    path('order/<int:pk>', views.Order_detail, name='order-detail'),

    path('add-item', views.ItemAdd.as_view(), name='item-add'),
    path('order-conf', views.orderConf, name='order-conf'),

    path('Myorder', views.MyorderConf, name='Myorder'),



    path('order-conf-ajax', views.orderConfajax, name='order-conf-ajax'),
]
