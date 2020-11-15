import random
import string
import datetime
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, request
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, View, CreateView, DeleteView, UpdateView
from search_views.filters import BaseFilter
from search_views.views import SearchListView
from django.contrib.auth import update_session_auth_hash
from utente.forms import RegisterForm
from utente.models import User
from .forms import CheckoutForm, PaymentForm, BookingForm, SearchForm, AddressForm, ItemCrispyForm,ReviewForm
from .models import Item, OrderItem, Order, Address, Payment, Gallery, Booking, Profile,Reviews

stripe.api_key = settings.STRIPE_SECRET_KEY



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def homepageqq(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:order-conf')

        try:
            Profile.objects.get(user=request.user)
            return redirect('core:home')
        except Profile.DoesNotExist:
            return redirect('core:address-add')
    return redirect('core:home')

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
    success_url = reverse_lazy('core:address-add')


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
            mylist = ["1","2","3","4","5","9","x","a" ]

            random.shuffle(mylist)
            str1 = ''.join(mylist)
            order.ref_code=str1
            order.save()
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
                        #shipping_address.save()
                        order.shipping_address = Address.objects.get(profile__user=self.request.user)
                        #order.shipping_address = shipping_address
                        order.ordered=True
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
                    return redirect('core:LocalPayment')

                elif payment_option == 'P':
                    return redirect('core:LocalPayment')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


def LocalPayment(request):
    # create the payment
    user = request.user
    new_or = Order.objects.get(user=user, ordered=False)
    payment = Payment()
    payment.code = "local"
    payment.user = request.user
    payment.amount = new_or.get_total()
    payment.save()
    new_or.shipping_address=Address.objects.get(profile__user=user)
    new_or.payment=payment
    new_or.ordered=True
    new_or.save()
    return redirect('core:home')

def Cpayment(request):
    # create the payment
    user = request.user
    new_or = Order.objects.get(user=user, ordered=False)
    payment = Payment()
    payment.code = "Paypal"
    payment.user = request.user
    payment.amount = new_or.get_total()
    payment.save()

    new_or.shipping_address=Address.objects.get(profile__user=user)
    new_or.payment=payment
    new_or.ordered=True
    new_or.save()
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
def add_review(request,slug):
    item = get_object_or_404(Item, slug=slug)
    created = Reviews.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    if request.method == 'POST' and request.user.is_authenticated:
        customer = request.user
        item = get_object_or_404(Item, slug=slug)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=True)
            review.user = User.objects.get(user_id=request.user.id)
            review.product=Item.objects.get(item__slug=item.slug)
            messages.success(request, 'Aggiunto al revie!')
            review.save()
        #else:
        #    messages.error(request, 'Salvataggio non ha avuto successo!')
        return redirect('core:home')
    else:
        form = ReviewForm()
    context = {'form':form }
    return render(request, 'addReview.html', context)



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
            messages.success(request, 'Aggiunto al booking!')
            booking.save()
        #else:
        #    messages.error(request, 'Salvataggio non ha avuto successo!')
        return redirect('core:booking')
    else:
        form = BookingForm()
    context = {'form':form }
    return render(request, 'booking.html', context)


    """

        form = BookingForm(request.POST)
        print(str(request.POST.get('date_start')).split("/"))
        a = str(request.POST.get('date_start')).split(" ")
        b = a[1].split(":")
        a = a[0].split("/")
        print(a, b)
        object_list = Booking.objects.filter(date_start__day=a[0], date_start__month=a[1], date_start__year=a[2])
        # datetime.date(2005, 1, 3)
        print(sum(object_list.values_list('chair', flat=True)))

        if form.is_valid() and sum(object_list.values_list('chair', flat=True)) < 40:
            """

class BookingDelete(SuccessMessageMixin,DeleteView):
    model = Booking
    template_name = 'delete.html'
    success_url = reverse_lazy('core:profile')

class AdressDelete(SuccessMessageMixin,DeleteView):
    model = Address
    template_name = 'deleteAdress.html'
    success_url = reverse_lazy('core:home')


class AddressList(ListView):
    model = Address
    template_name = 'address/address_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        user=self.request.user
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['object_list'] = Profile.objects.get(user=user).address.all()
        return context

@login_required(login_url='/login')
def ProfileView(request):
    form = []
    user=request.user.id
    print(user)
    #UserProfile.objects.get()
    context1 = {"profile": Profile.objects.get(user=request.user)}
    if (request.user.is_staff):
        form = Booking.objects.all()
        form.order_by('date_start','+time')
    else:
        form=Booking.objects.filter(user_id=user)

    context={'form':form}
    return render(request, 'profile.html', context,context1 )



def contatti(request):
    return render(request, 'contatti.html')


class PasswordChange(object):
    pass


@login_required(login_url='/login')

def PasswordChangeView(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {
        'form': form
    })

@login_required(login_url='/login')
def booking(request):
    if request.method == 'POST' and request.user.is_authenticated:
        customer = request.user
        form = BookingForm(request.POST)
        print("#######################################################################")
        print(str(request.POST.get('date_start')).split("/"))
        a = str(request.POST.get('date_start')).split(" ")
        b = a[1].split(":")
        a = a[0].split("/")
        print(a, b)
        object_list = Booking.objects.filter(date_start__day=a[0], date_start__month=a[1], date_start__year=a[2])
        print(sum(object_list.values_list('chair', flat=True)))



        if form.is_valid() and sum(object_list.values_list('chair', flat=True)) < 10:
            booking = form.save(commit=True)
            #booking.date_start = timezone.now()
            booking.user=customer
            booking.save()
            profile = Profile.objects.get(user=customer)
            profile.booking.add(booking)
            profile.save()
            messages.success(request, 'Aggiunto al booking!')
        else:
            messages.error(request, 'Salvataggio non ha avuto successo!')

        #return redirect('core:home')
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
            #address.user=customer
            address.save()

            try:
                profile = Profile.objects.get(user=customer)
                profile.address.add(address)
                profile.save()
                print("update adrss")
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=customer)
                profile.address.add(address)
                profile.save()
                print("new adress")

            # print('profile:'+profile+'address_profile:'+profile.address.all())

        return redirect('core:home')
    else:
        form = AddressForm()
    context = {'form':form }
    return render(request, 'address_add.html', context)



@login_required
def address_detail(request, pk):
    template_name = 'address_detail.html'
    addr = Address.objects.get(pk=pk)
    profile = get_object_or_404(Profile,user=request.user,address=addr)
    return render(request, template_name=template_name, context={'object': addr,'profile':profile})


@method_decorator(login_required, name='dispatch')
class AddressList(ListView):
    model = Address
    template_name = 'address_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        user=self.request.user
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['object_list'] = Profile.objects.get(user=user).address.all()
        return context




@method_decorator(login_required, name='dispatch')
class AddressChange(UpdateView):

    model = Address
    template_name = 'address_add.html'
    form_class = AddressForm
    success_url = reverse_lazy('core:profile')

    def form_valid(self, form):
        addr=form.save()
        user = self.request.user
        profile=Profile.objects.get(user=user)
        profile.address.add(addr)
        profile.save()
        return super(AddressChange, self).form_valid(form)

    def get_context_data(self, **kwargs):
        user=self.request.user
        addr=self.object
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        #context['object_list'] = Profile.objects.get(user=user).address.all()
        get_object_or_404(Profile, user=user, address=addr)
        return context

def is_restaurateur(args):
    pass


method_decorator(is_restaurateur, name='dispatch')
class ItemAdd(CreateView):
    model = Item
    template_name = 'add-item.html'
    form_class = ItemCrispyForm
    success_url = reverse_lazy('core:home')


def orderConfajax(request):
    #product = Product.objects.get(id=id)
    #print(request.POST.get('username'))
    data = { 'is_taken': False }
    if request.method == 'POST' and request.user.is_authenticated:

        tt = Order.objects.get(id=request.POST.get('username'))
        tt.confirmOrder = True
        tt.save()

        data = { 'is_taken': True }

        return JsonResponse(data)
    return JsonResponse(data)


@login_required(login_url='/login')
def orderConf(request):
    now  = datetime.datetime.now()
    start_date = now.strftime("%m")
    start_date=str(int(start_date)-1)

    print(start_date, "startdate")
    items = {}
    for x in Order.objects.filter(ordered_date__month=start_date):
        items[int(x.ordered_date.strftime("%d"))] = 0

    for x in Order.objects.filter(ordered_date__month=start_date):
        items[int(x.ordered_date.strftime("%d"))] = x.items.count() + items[int(x.ordered_date.strftime("%d"))]

    list = [(k, v) for k, v in items.items()]
    print(items)

    norder = Order.objects.filter(confirmOrder = False)

    context = {'items': list, 'norder' : norder}
    return render(request, 'grafico.html', context)


@login_required(login_url='/login')
def MyorderConf(request):
    norder = Order.objects.filter(user = request.user)
    context = {'norder' : norder}
    return render(request, 'myorder.html', context)


