from django.shortcuts import render, redirect
from django.views.generic import FormView, CreateView, DetailView, ListView
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from .forms import UserAddressForm, AddressForm
from .models import UserAddress, UserCheckout, Order
from .mixins import LoginRequiredMixin, CartOrderMixin
# Create your views here.

class OrderDetail(DetailView):
    model = Order

    def dispatch(self, request, *args, **kwargs):
        try:
            user_check_id = self.request.session.get("user_checkout_id")
            user_checkout = UserCheckout.objects.get(id=user_check_id)
        except UserCheckout.DoesNotExist:
            user_checkout = UserCheckout.objects.get(user=request.user)
        except:
            user_checkout = None

        obj = self.get_object()
        print(obj)
        print(obj.user)
        if obj.user == user_checkout and user_checkout is not None:
            return super(OrderDetail, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404

class OrderList(LoginRequiredMixin, ListView):
    model = Order

    def get_queryset(self):
        user_check_id = self.request.user.id
        user_checkout = UserCheckout.objects.get(user__id=user_check_id)
        print(super(OrderList, self).get_queryset().filter(user=user_checkout))
        return super(OrderList, self).get_queryset().filter(user=user_checkout)

class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = "forms.html"
    success_url = "/checkout/address/"

    def get(self, request, *args, **kwargs):
        get_data = super(UserAddressCreateView, self).get(request, *args, **kwargs)
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id == None:
            return redirect('checkout')

        return get_data

    def get_context_data(self, *args, **kwargs):
        context = super(UserAddressCreateView,
                        self).get_context_data(*args, **kwargs)
        context['title'] = 'Add Your Address'
        return context

    def get_checkout_user(self):
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        return user_checkout

    def form_valid(self, form, *args, **kwargs):
        form.instance.user = self.get_checkout_user()
        return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)


class AddressSelectFormView(CartOrderMixin, FormView):
    form_class = AddressForm
    template_name = 'orders/address_select.html'

    def get(self, request, *args, **kwargs):
        get_data = super(AddressSelectFormView, self).get(request, *args, **kwargs)
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id == None:
            return redirect('checkout')

        return get_data

    def dispatch(self, *args, **kwargs):
        user_check_id = self.request.session.get("user_checkout_id")
        print(user_check_id)
        if user_check_id is None:
            return redirect("checkout")
        b_address, s_address = self.get_addresses()
        if b_address.count() == 0:
            messages.success(
                self.request, "Please add a billing address before continuing")
            return redirect("user_address_create")
        elif s_address.count() == 0:
            messages.success(
                self.request, "Please add a shipping address before continuing")
            return redirect("user_address_create")
        else:
            return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

    def get_addresses(self, *args, **kwargs):
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        b_address = UserAddress.objects.filter(
            user=user_checkout,
            type='billing',
        )
        s_address = UserAddress.objects.filter(
            user=user_checkout,
            type='shipping',
        )
        return b_address, s_address

    def get_form(self, *args, **kwargs):
        form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
        b_address, s_address = self.get_addresses()

        form.fields["billing_address"].queryset = b_address
        form.fields["shipping_address"].queryset = s_address
        return form

    def form_valid(self, form, *args, **kwargs):
        billing_address = form.cleaned_data["billing_address"]
        shipping_address = form.cleaned_data["shipping_address"]
        order = self.get_order()
        order.billing_address = billing_address
        order.shipping_address = shipping_address
        order.save()
        return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse("checkout")