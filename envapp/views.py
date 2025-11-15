from django.shortcuts import render,redirect , get_object_or_404
from .models import Product , Cart , Order
from .forms import AddForm, RegistrationForm , LoginForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.urls import reverse


stripe.api_key = settings.STRIPE_SECRET_KEY







# Create your views here.

def home(request):
    return render(request,'home.html')

def contact(request):
    return render(request,'contact.html')




@login_required
def view_item(request):
    items=Product.objects.all()
    return render(request,'items.html',{'item':items})

@login_required
def Add_item(request):
    form=AddForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('PRODUCTS')
    return render(request,'itemsform.html',{'forms':form})

@login_required
def update_item(request,id):
    item=Product.objects.get(id=id)
    form=AddForm(request.POST or None,request.FILES or None ,instance=item)
    if form.is_valid():
        form.save()
        return redirect('PRODUCTS')
    return render(request,'update_item.html',{'form':form})

@login_required
def delete_book(request,id):
    item=Product.objects.get(id=id)
    if request.method=='POST':
        item.delete()
        return redirect('PRODUCTS')
    return render(request,'confirm_delete.html',{'item':item})

def register(request):
    form=RegistrationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save()
        return redirect('loginpage')
    return render(request,'registration.html',{'form':form})

def login_user(request):
    form=LoginForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.get_user()
        login(request,user)
        return redirect('PRODUCTS')
    return render(request,'login.html',{'abc':form})


def logout_user(request):
    logout(request)
    return redirect('loginpage')


@login_required
def add_to_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)
    if not created:
        cart_item.quantity +=1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items=Cart.objects.filter(user=request.user)
    total_price=0
    for item in cart_items:
        total_price += item.product.price * item.quantity
    return render (request, 'view_cart.html', {'cart_items':cart_items,'total_price': total_price})

def remove_from_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    cart_item=Cart.objects.get(product=product,user=request.user)
    if cart_item.quantity >1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('view_cart')


# def items_page(request):
#     query = request.GET.get('q', '')
#     category_id = request.GET.get('category', '')

#     items = Item.objects.all()

#     # Search by name or description
#     if query:
#         items = items.filter(name_icontains=query) | items.filter(description_icontains=query)

#     # Filter by category
#     if category_id:
#         items = items.filter(category__id=category_id)

#     categories = Category.objects.all()
#     return render(request, 'items.html', {
#         'item': items,
#         'categories': categories,
#     })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-Ordered_at')
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def place_order(request):
    if request.method == "POST":
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return redirect('view_cart')

        # Total calculation
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        total_quantity = sum(item.quantity for item in cart_items)
        product_names = ", ".join([item.product.name for item in cart_items])

        # Save orders locally
        for cart_item in cart_items:
            Order.objects.create(
                user=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                address=address,
                payment_method=payment_method,
            )

        # If COD, don't use Stripe
        if payment_method == "COD":
            cart_items.delete()
            return render(request, "success.html", {
                "message": "✅ Order placed successfully with Cash on Delivery!"
            })

        # ✅ Stripe session creation (correct indentation)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': f"Order: {product_names}"},
                    'unit_amount': int(total_amount * 100 / total_quantity),
                },
                'quantity': total_quantity,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cancel')),
        )

        # cart_items.delete()  # optional: you can delete after a successful payment
        return redirect(session.url)

    return redirect('view_cart')


@login_required
def payment_success(request):
    # Clear cart only after successful payment
    Cart.objects.filter(user=request.user).delete()
    return render(request, 'success.html', {
        "message": "✅ Payment successful! Your order has been confirmed."
    })

@login_required
def payment_cancel(request):
    return render(request, 'cancel.html', {
        "message": "❌ Payment canceled. Your cart is still saved."
    })



# def payment_success(request):
#     return render(request, 'success.html')


# def payment_cancel(request):
#     return render(request, 'cancel.html')


def buy_now(request,product_id):
    cart_items=Cart.objects.filter(user=request.user,product_id=product_id)
    if not cart_items.exists():
        return redirect('view_cart')
    product=get_object_or_404(Product,id=product_id)

    total_quantity= sum(item.quantity for item in cart_items)

    session=stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data':{
                    'currency':'inr',
                    'product_data':{
                        'name':product.name,
                    },
                    'unit_amount': int(float(product.price)*100),


                },
                'quantity':total_quantity,
            }
        ],
        mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cancel')),
      )
    return redirect(session.url)

def payment_success(request):
    return render(request,'success.html')

def payment_cancel(request):
    return render(request,'cancel.html')


@login_required
def buy_now1(request, product_id=None):
    if request.method == "POST":
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return redirect('view_cart')

        # Calculate total price for all products
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        total_quantity = sum(item.quantity for item in cart_items)
        product_names = ", ".join([item.product.name for item in cart_items])

        # ✅ Save order before payment
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                address=address,
                payment_method=payment_method
            )

        # ✅ Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': f"Order: {product_names}"},
                    'unit_amount': int(total_amount * 100 / total_quantity),
                },
                'quantity': total_quantity,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cancel')),
        )

        # ✅ Clear cart
        cart_items.delete()

        return redirect(session.url)

    return redirect('view_cart')



def payment_success(request):
    return render(request, 'success.html')


def payment_cancel(request):
    return render(request, 'cancel.html')