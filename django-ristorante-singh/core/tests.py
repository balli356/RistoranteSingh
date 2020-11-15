from django.test import TestCase

# Create your tests here.

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


# test view
from core.forms import BookingForm
from core.models import *


class TestViews(TestCase):

    def setUp(self):
        self.user_test = User.objects.create(email='test@test.it',first_name='test_user',
                                             last_name='test_last',password='test')
        self.items=Item.objects.create(title='title',price=5,category='D',label='P',
                                       slug='S',description="ciao")
        self.booking=Booking.objects.create(user=self.user_test,description='ciao',
                                            chair=3,title='nomePersona',date_start='2020-12-1 16:00')
        self.booking.save()



    def test_model(self):
        item_test = Item()
        item_test.title = "test da prova"
        item_test.price = 5
        item_test.category = 'A'
        item_test.label = 'P'
        item_test.slug = "sl"
        item_test.description="descrizione"
        item_test.save()
        record = Item.objects.get(id=item_test.id)
        self.assertEqual(record, item_test)


    def test_order_item(self):
        order_item_test = OrderItem()
        order_item_test.user = self.user_test
        order_item_test.ordered = True
        order_item_test.item= self.items
        order_item_test.quantity = 4
        order_item_test.save()
        record = OrderItem.objects.get(pk=order_item_test.pk)
        self.assertEqual(record, order_item_test)

    def test_address(self):
        address_test = Address()
        address_test.user = self.user_test
        address_test.città="Modena"
        address_test.cap="2000"
        address_test.n_civico="28"
        address_test.via="della pace"
        address_test.piano="2"
        address_test.save()
        record = Address.objects.get(pk=address_test.pk)
        self.assertEqual(record, address_test)






    def test_crea_booking_non_valido(self):
        """
            form non valido per la creazione di una Prenotayione , numero dei posti = 0,
            deve ritornare False
        """
        form = BookingForm( data={
            'title': 'prenoto per 5',
            'description': 'descrizione',
            'chair': 0,
            'date_start': '2222-12-05 16:00'
        })
        self.assertEqual(form.is_valid(), False)


    def test_crea_booking_valido(self):
        """
            form non valido per la creazione di una Prenotayione , numero dei posti = 0,
            deve ritornare False
        """
        form = BookingForm(data={
            'title': 'prenoto per 5',
            'description': 'descrizione',
            'chair': 2,
            'date_start': '12/12/2021 16:00'
        })
        self.assertEqual(form.is_valid(), True)

    def test_address_add(self):
        self.client.login(email='admin@admin.it', password='Balli1994')
        url = reverse('core:address-add')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_login(self):
        self.client.login(email='admin@admin.it', password='Balli1994')
        response = self.client.get(reverse('core:logout'))
        self.assertEquals(response.status_code, 302)

        # Testo che la pagina di visualizzazione del profile venga caricata correttamente
    def test_profile_view(self):
        self.client.login(email='test@test.it', password='test')
        response = self.client.get(reverse('core:profile'))
        self.assertEquals(response.status_code, 302)
