import random
import string
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, CreateView, DeleteView
from search_views.filters import BaseFilter
from search_views.views import SearchListView
from django.contrib.auth import update_session_auth_hash
from utente.forms import RegisterForm
from utente.models import User
from .forms import CheckoutForm, PaymentForm, BookingForm, SearchForm, AddressForm
from .models import Item, OrderItem, Order, Address, Payment, Gallery, Booking, Profile

stripe.api_key = settings.STRIPE_SECRET_KEY



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

"""def homepageqq(request):
    print("is_admin")
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin')
        else:
            return redirect('core:home')
    return redirect('core:home')"""

def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid



class UserCreateView(CreateView):
    #form_class = UserCreationForm
    form_class = RegisterForm
    template_name = 'registration/user_create.html'
    success_url = reverse_lazy('core:home')



class LoginViewwe(LoginView):
    """
    Display the login form and handle the login action.
    """
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('core:home')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    civico=form.cleaned_data.get('shipping_civic')
                    florr=form.cleaned_data.get('shipping_floor')
                    city=form.cleaned_data.get('shipping_city')

                    if is_valid_form([shipping_address1,  shipping_zip]):
                        User.objects.filter()

                        shipping_address = Address(
                            user=self.request.user,
                            cap=shipping_zip,
                            città=city,
                            via=shipping_address1,
                            n_civico=civico,
                            piano=florr,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()


                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")


                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:LocalPayment',pk=1)
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


def LocalPayment(request,pk):
    user = request.user
    ord=Order.objects.get(pk=pk)
    print(Address.objects.filter(user=user))
    ord.shipping_address=Address.objects.get(profile__user=user)
    #ord.is_confirmed_by_restaurateur=False
    #ord.is_confirmed_by_client=False
    #ord.is_edited_by_restaurateur=False
    #ord.is_finished=True
    ord.ordered=True
    ord.save()
    return redirect('core:home')

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.shipping_address:
            context = {
                'order': order,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user

            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a shipping address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = User.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="euro",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="euro",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required(login_url='/login')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required(login_url='/login')
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required(login_url='/login')
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)



class ItemFilter(BaseFilter):
    search_fields = {
        'search_item': ['title']
    }
class ItemSearchList(SearchListView):
    model = Item
    paginate_by = 30
    template_name = "core/item_list"
    form_class = SearchForm
    filter_class = ItemFilter

def articolo_alternative(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            items=Item.objects.filter(title__contains=form.cleaned_data.get('search_item'))
            context = {
                'items': items
            }
            return render(request, 'searchHome.html', context)  # rimanda alla pagina di inserimento

    else:
        form = SearchForm()
    context = {'form': form}
    return render(request, 'item_list.html', context)





def CategoryFilter(request,cat):
    object_list = Item.objects.filter(category=cat)
    context = {
        'object_list': object_list
    }
    return render(request, 'home.html', context)

@login_required(login_url='/login')
def booking(request):
    if request.method == 'POST' and request.user.is_authenticated:
        customer = request.user
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=True)
            #booking.date_start = timezone.now()
            booking.user = User.objects.get(user_id=request.user.id)
            booking.save()
        return redirect('core:home')
    else:
        form = BookingForm()
    context = {'form':form }
    return render(request, 'booking.html', context)

class BookingDelete(SuccessMessageMixin,DeleteView):
    model = Booking
    template_name = 'delete.html'
    success_url = reverse_lazy('core:profile')

@login_required(login_url='/login')
def ProfileView(request):
    form = []
    user=request.user.id
    print(user)
    #UserProfile.objects.get()
    form=Booking.objects.filter(user_id=user)
    print(form)
    context={'form':form}
    return render(request, 'profile.html', context)

def contatti(request):
    return render(request, 'contatti.html')


class PasswordChange(object):
    pass


@login_required(login_url='/login')
def PasswordChangeView(request):

    if request.method == 'POST':
        form = PasswordChange(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('core:home')
    else:
        print("dopo")
        #form = PasswordChange(request.user)
    return render(request, 'password_change.html', {'form': form})

@login_required(login_url='/login')
def booking(request):
    if request.method == 'POST' and request.user.is_authenticated:
        customer = request.user
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=True)
            #booking.date_start = timezone.now()
            booking.user=customer
            booking.save()
        return redirect('core:home')
    else:
        form = BookingForm()

    context = {'form':form }
    return render(request, 'booking.html', context)


def gallery(request):
    context= {
        'photos':  Gallery.objects.all()
    }
    return render(request, 'gallery.html',context )




@login_required(login_url='/login')
def AddressAdd(request):
    if request.method == 'POST' and request.user.is_authenticated:
        customer = request.user
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=True)
            #booking.date_start = timezone.now()
            address.user=customer
            address.save()
            profile = Profile.objects.create(user=customer)
            profile.address.add(address)
            profile.save()
            # print('profile:'+profile+'address_profile:'+profile.address.all())

        return redirect('core:home')
    else:
        form = AddressForm()
    context = {'form':form }
    return render(request, 'address_add.html', context)


"""
class AddressAdd(CreateView):
    modelpyt = Address
    template_name = 'address/address_add.html'
    form_class = AddressForm
    # fields = ('first_name', 'middle_name', 'last_name')
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        addr=form.save(commit=True)
        addr.user=self.request.user.id
        addr.save
        return super(AddressAdd, self).form_valid(form)
  
"""





"""
method_decorator(is_restaurateur, name='dispatch')
class PizzaAdd(CreateView):
    model = Pizza
    template_name = 'restaurateur/pizza/add.html'
    form_class = PizzaCrispyForm
    success_url = reverse_lazy('order:restaurateur-pizza-list')
    
    
@login_required
def list_orders_user(request):
    list_orders=Order.objects.filter(Q(user=request.user)&(Q(is_finished=True)|Q(is_deleted=True))).order_by('-timestamp_click__date','-time')
    return render(request=request, template_name='client/order/list.html', context={'list_orders':list_orders})


@login_required
def order_done(request,pk):
    obj = Order.objects.get(pk=pk)
    obj.is_confirmed_by_restaurateur=True
    obj.is_confirmed_by_client=True
    obj.is_edited_by_restaurateur=False
    obj.save()
    return render(request=request, template_name='client/order/done.html', context={'order':obj,'user':request.user})

def str_ranking(ranking):
    s = '<ul>'
    for i in ranking:
        s+='<li>'+str(i[0])+' - comprato '+str(i[1])+' volte</li>'
    s+='</ul>'
    if len(ranking)==0:
        return ''
    return s

'''
    Funzione che serve per ritornare le statistiche degli elementi più venduti.
'''
def get_ranked_statistics(str_start_date='',str_end_date=''):
    start_date=datetime.strptime('2000-01-01','%Y-%m-%d') if str_start_date=='' else datetime.strptime(str_start_date,'%Y-%m-%d')
    end_date=datetime.today().date() + timedelta(days=1) if str_end_date=='' else datetime.strptime(str_end_date,'%Y-%m-%d')
    orders_confirmed = Order.objects.filter(Q(timestamp_click__gte=start_date) & Q(timestamp_click__lte=end_date) & (Q(is_finished=True)))
    total = sum([o.price() for o in orders_confirmed])
    ranking_cheese={}
    for order in orders_confirmed:
        for o_pizza in order.order_pizza.all():
            for cheese in o_pizza.pizza.cheese.all():
                ranking_cheese[cheese] = ranking_cheese.get(cheese, 0) + 1
        for pizza in order.personalized_pizza.all():
            for cheese in pizza.cheese.all():
                ranking_cheese[cheese] = ranking_cheese.get(cheese, 0) + 1
    ranking_cheese = sorted(ranking_cheese.items(), key=lambda x: x[1], reverse=True)
    ranking_toppings={}
    for order in orders_confirmed:
        for o_pizza in order.order_pizza.all():
            for topping in o_pizza.pizza.toppings.all():
                ranking_toppings[topping] = ranking_toppings.get(topping, 0) + 1
        for pizza in order.personalized_pizza.all():
            for topping in pizza.toppings.all():
                ranking_toppings[topping] = ranking_toppings.get(topping, 0) + 1
    ranking_toppings = sorted(ranking_toppings.items(), key=lambda x: x[1], reverse=True)
    ranking_pizza={}
    for order in orders_confirmed:
        for o_pizza in order.order_pizza.all():
            ranking_pizza[o_pizza.pizza]=ranking_pizza.get(o_pizza.pizza,0)+1
    ranking_pizza = sorted(ranking_pizza.items(), key=lambda x: x[1], reverse=True)
    return str_ranking(ranking_cheese),str_ranking(ranking_toppings),str_ranking(ranking_pizza),total

'''
    View che serve al ristoratore per visualizzare le statistiche degli elementi più venduti
'''
@is_restaurateur
def show_statistics(request): #(request,data_inizio=1970,data_fine=today)
    ranking_cheese, ranking_toppings, ranking_pizza, total=get_ranked_statistics()
    return render(request=request, template_name='restaurateur/statistics/show.html', context={'total': total,
                                                                                               'ranking_toppings':ranking_toppings,
                                                                                               'ranking_cheese':ranking_cheese,
                                                                                            'ranking_pizza':ranking_pizza})

'''
    View ajax che serve al ristoratore a filtrare le statistiche in base alla data.
'''
@is_restaurateur
def ajax_filter_statistics(request):
    str_start_date=request.GET.get('start_date',None)
    str_end_date=request.GET.get('end_date',None)
    ranking_cheese,ranking_toppings,ranking_pizza,total=get_ranked_statistics(str_start_date=str_start_date,str_end_date=str_end_date)
    return JsonResponse({'ranking_cheese':ranking_cheese,'ranking_toppings':ranking_toppings,'ranking_pizza':ranking_pizza,'total':total})

"""