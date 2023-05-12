from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.db.models import Q
from products.models import ProductFeatured, Product, Variation
from utily.models import History
from .forms import ContactForm, SignUpForm
from .models import SignUp

# Create your views here.
def home(request):
	title = 'Sign Up Now'
	featured_image = ProductFeatured.objects.filter(Q(active=True) & Q(upload_to_jumbotron=True))
	latestproduct = Product.objects.all().order_by("-id")[:8]
	products = Product.objects.all().order_by("?")[:6]
	products2 = ProductFeatured.objects.all().filter(active=True).order_by("?")[:6]
	top_seller = Variation.objects.all().filter(sold_bill__gte=0).order_by("-sold_bill")[:5]
	if request.user.is_authenticated:
		histories = History.objects.all().filter(user=request.user).order_by("-id")[:5]
	else:
		histories = request.session.get('history')
	history = request.session.get('history_ids')
	hs1 = []
	if history is not None:
		history.reverse()
		for hs in history:
			hstory = Product.objects.get(id=hs)
			hs1.append(hstory)

	form = SignUpForm(request.POST or None)
	if form.is_valid():
		instance = form.save(commit=False)
		full_name = form.cleaned_data.get("full_name")
		if not full_name:
			full_name = "New full name"
		instance.full_name = full_name
		instance.save()
		context = {
			"title": "Thank you"
		}

	if request.user.is_authenticated and request.user.is_staff:
		queryset = SignUp.objects.all().order_by('-timestamp') #.filter(full_name__iexact="Justin")
		#print(SignUp.objects.all().order_by('-timestamp').filter(full_name__iexact="Justin").count())
		context = {
			"queryset": queryset
		}

	context = {
		"title": title,
		"featured_image" : featured_image,
		"products" : products,
		"latestproduct" : latestproduct,
		"products2" : products2,
		"topselller" : top_seller,
		"histories" : histories,
		"form": form,
		"history" : hs1
	}

	return render(request, "home.html", context)



def contact(request):
	title = 'Contact Us'
	title_align_center = True
	form = ContactForm(request.POST or None)
	if form.is_valid():
		# for key, value in form.cleaned_data.iteritems():
		# 	print key, value
		# 	#print form.cleaned_data.get(key)
		form_email = form.cleaned_data.get("email")
		form_message = form.cleaned_data.get("message")
		form_full_name = form.cleaned_data.get("full_name")
		# print email, message, full_name
		subject = 'Site contact form'
		from_email = settings.EMAIL_HOST_USER
		to_email = [from_email, 'youotheremail@email.com']
		contact_message = "%s: %s via %s"%(
				form_full_name,
				form_message,
				form_email)
		some_html_message = """
		<h1>hello</h1>
		"""
		send_mail(subject,
				contact_message,
				from_email,
				to_email,
				html_message=some_html_message,
				fail_silently=True)

	context = {
		"form": form,
		"title": title,
		"title_align_center": title_align_center,
	}
	return render(request, "forms.html", context)
















