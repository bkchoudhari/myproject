from django.shortcuts import render,redirect
from .models import User,Cloth,Contact,Wishlist,Cart,Transaction
from django.http import JsonResponse
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
       
		amount = int(request.POST['amount'])

	except:
		return render(request, 'index.html', context={'error': 'Wrong Accound Details or amount'})

	transaction = Transaction.objects.create(made_by=user,amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY

	params = (
		('MID', settings.PAYTM_MERCHANT_ID),
		('ORDER_ID', str(transaction.order_id)),
		('CUST_ID', str(user.email)),
		('TXN_AMOUNT', str(transaction.amount)),
		('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
		('WEBSITE', settings.PAYTM_WEBSITE),
		# ('EMAIL', request.user.email),
		# ('MOBILE_N0', '9911223388'),
		('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
		('CALLBACK_URL', 'http://localhost:8000/callback/'),
		# ('PAYMENT_MODE_ONLY', 'NO'),
	)
	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)

	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user,payment_status="pending")
	for i in carts:
		i.payment_status="completed"
		i.save()
	
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)




@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return redirect('cart')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status="completed")
	return render(request,'myorder.html',{'carts':carts})

def search(request):
	if request.method=="POST":
		search_cloth=request.POST['Search_cloth']
		all_cloth=Cloth.objects.filter(cloth_brand=search_cloth)
		return render(request,'search.html',{'all_cloth':all_cloth})
	else:
		return render(request,'search.html ')


def validate_email(request):
	email=request.GET.get('email')
	data={
	'is_email':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)


def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="user":
			return render(request,'index.html')
		elif user.usertype=="seller":	
			return render(request,'seller_index.html')
	except:
		return render(request,'index.html')


def sellr_index(request):
	return render(request,'seller_index.html')	

def shop(request):
	all_cloth=Cloth.objects.all()
	return render(request,'shop.html',{'all_cloth':all_cloth})

def product_details(request):
	return render(request,'product-details.html')	

def checkout(request):
	return render(request,'checkout.html')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status="pending")
	for i in carts:
		net_price=net_price+i.total_price

	request.session['cart_count']=len(carts)

	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'],password=request.POST['password'])
			if user.usertype=="user":
				request.session['fname']=user.fname
				request.session['email']=user.email
				wishlist=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlist)
				carts=Cart.objects.filter(user=user)
				request.session['cart_count']=len(carts)
				return render(request,'index.html')
			elif user.usertype=="seller":
				request.session['fname']=user.fname
				request.session['email']=user.email
				return render(request, 'seller_index.html')	
		except Exception as e:
			print(e)
			msg="email or password is incorrect"
			return render(request,'login.html',{'msg':msg})
	else:			
		return render(request,'login.html')

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Already Register"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword'],
					address=request.POST['address'],
					)
				msg="User sign up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password and confirm password does not matched"
				return render(request,'signup.html',{'msg':msg})	

	else:	
		return render(request,'signup.html')	

def blog(request):
	return render(request,'blog.html')

def blog_single(request):
	return render(request,'blog-single.html')



def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				message=request.POST['message']
			)
		msg="Contact Saved Successfully"
		return render(request,'contact.html',{'msg':msg})
	else:
		return render(request,'contact.html')

def logout(request):
	try:
		del request.session['fname']
		del request.session['email']
		del request.session['wishlist_count']
		del request.session['cart_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')


def add_clothes(request):
	if request.method=="POST":
		cloth_seller=User.objects.get(email=request.session['email'])
		Cloth.objects.create(
				cloth_seller=cloth_seller,
				cloth_brand=request.POST['cloth_brand'],
				cloth_price=request.POST['cloth_price'],
				cloth_image=request.FILES['cloth_image'],
				cloth_desc=request.POST['cloth_desc'],
			)
		msg="cloth add Successfully"
		return render(request,'add_clothes.html',{'msg':msg})

	else:	
		return render(request,'add_clothes.html')

def view_clothes(request):
	cloth_seller=User.objects.get(email=request.session['email'])
	clothes=Cloth.objects.filter(cloth_seller=cloth_seller)
	print(clothes)
	return render(request,'view_clothes.html',{'clothes':clothes})

def seller_index(request):
	return render(request,'seller_index.html')

def cloth_detail(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	return render(request,'cloth_detail.html',{'cloth':cloth})	

def user_cloth_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	user=User.objects.get(email=request.session['email'])
	cloth=Cloth.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,cloth=cloth)
		wishlist_flag=True
	except:
		pass
	try:
		Cart.objects.get(user=user,cloth=cloth)
		cart_flag=True
	except:
		pass		
	return render(request,'user_cloth_detail.html',{'cloth':cloth,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})	


def cloth_edit(request,pk):	
	cloth=Cloth.objects.get(pk=pk)
	if request.method=="POST":
		cloth.cloth_brand=request.POST['cloth_brand']
		cloth.cloth_desc=request.POST['cloth_desc']
		cloth.cloth_price=request.POST['cloth_price']
		try:
			cloth.cloth_image=request.FILES['cloth_image']
		except:
			pass
		cloth.save()
		return render(request,'cloth_detail.html',{'cloth':cloth})	
	else:
		return render(request,'cloth_edit.html',{'cloth':cloth})

def cloth_delete(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	cloth.delete()
	return redirect('view_clothes')

def add_to_wishlist(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(
		user=user,
		cloth=cloth

		)
	return redirect('wishlist')	

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})


def remove_from_wishlist(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,cloth=cloth)
	wishlist.delete()
	return redirect('wishlist')


def add_to_Cart(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
		user=user,
		cloth=cloth,
		price=cloth.cloth_price,
		total_price=cloth.cloth_price
		)
	return redirect('cart')

def remove_from_cart(request,pk):
	cloth=Cloth.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,cloth=cloth)
	cart.delete()
	return redirect('cart')

def change_qty(request):
	cart=Cart.objects.get(pk=request.POST['cart_id'])
	qty=int(request.POST['qty'])
	cart.qty=qty
	cart.total_price=qty*cart.price
	cart.save()
	return redirect('cart')	
