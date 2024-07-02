from django.shortcuts import render, HttpResponse,redirect
# Create your views here.
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login, logout
from .models import Product, Cart, Order
from django.db.models import Q 
import random
import razorpay
import pkg_resources
from django.core.mail import send_mail

def home(request):
    # userid=request.user.id  #check and return user id from database
    # print(userid)
    # print('result is:',request.user.is_authenticated) #check whether is user is login (T) else(false)

    # display all products in index file
    context={}
    p=Product.objects.filter(is_active=True)
    context['products']=p
    return render(request,'index.html',context)

def product_detail(request,pid):
    p=Product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_detail.html',context)


def register(request):
    if request.method=="POST":
      uname=request.POST['uname']
      upass=request.POST['upass']
      ucpass=request.POST['ucpass']
    #   User is inbuilt model/class from django.contrib.auth.models
    # just drop only one cmd migrate to create database rest of the part is same as msg project
      context={}
      if uname=='' or upass=='' or ucpass =='':
        context['errormsg']="Fields cannot be Empty"
      elif upass!=ucpass:
        context['errormsg']="Password and confirm password didn't match"
      else:
        try:
            u=User.objects.create(username=uname, email=uname, password=upass)
            u.set_password(upass)#hide password
            u.save()
            context['success']="User created Successfully, please login"
        except Exception:
            context['errormsg']="Username already Exist!!"
      return render(request,'register.html',context)
    else:
      return render(request,'register.html')

def user_login(request):
    if request.method=="POST":
       uname=request.POST['uname']
       upass=request.POST['upass']
       context={}
       if uname=='' or upass=='':
          context['errormsg']='Fields cannot be Empty'
          return render(request,'login.html',context)
       else:
          u=authenticate(username=uname, password=upass)
# authenticate : this function check username and password enterd by user with
# username and password in auth_user table and return object or row
          print(u) #object  
          # print(u.password)
          # print(u.is_superuser)
          # return HttpResponse('Data is Fetch')  
          if u is not None:
            login(request,u)
            return redirect('/')
          else:
             context['errormsg']='Invalid username and password'  
             return render(request,'login.html',context)                 
    else:    
      return render(request,'login.html')

def user_logout(request):
   logout(request)
   return redirect('/')


# sorting products categories vise
def catfilter(request,cv):
   q1=Q(cat=cv)
   q2=Q(is_active=True)
   p=Product.objects.filter(q1 & q2)
   context={}
   context['products']=p
   return render(request,'index.html',context)

# sort value range min to max andmax to min
def sort(request,sv):
  if sv=='0':
    # ascending
    col='price'
  else:
    # descending
    col='-price'
  p=Product.objects.order_by(col)
  context={}
  context['products']=p
  return render(request,'index.html',context)

# range between min and max value to sort items
def range(request):
   min=request.GET['min']
   max=request.GET['max']
  #  print(min, max)
  # price__gte= gtreater than equal, price__gt= greater than, price__lt= less than, price__lte=less than equal
   q1=Q(price__gte=min) #greater and equal than 1000
   q2=Q(price__lte=max)  #less and equal than 2000
   q3=Q(is_active=True)
   p=Product.objects.filter(q1&q2&q3)
   context={}
   context['products']=p
   return render(request,'index.html',context)

def addtocart(request,pid):
  if request.user.is_authenticated:
    userid= request.user.id 
    u=User.objects.filter(id=userid) #automatic user entry table 
    p=Product.objects.filter(id=pid) #product table
    q1=Q(uid=u[0])
    q2=Q(pid=p[0])
    c=Cart.objects.filter(q1&q2)
    n=len(c)
    context={}
    #to check product already add or not
    if n == 1:
      context['msg']='Product Already exist in cart!!'
    else:
      c=Cart.objects.create(uid=u[0],pid=p[0])
      c.save()
      context['success']='Product Added Successfully to cart!'
    context['products']=p
    return render(request,'product_detail.html',context)
    # return HttpResponse('product added in cart')
  else:
    return redirect('/login')
  
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id) 
    np= len(c)
    s=0
    for x in c:
       s= s + x.pid.price * x.qty
    context={}
    context['data']=c
    context['total'] =s
    context['n']=np
    return render(request,'cart.html',context)

def remove(request,cid):
   c=Cart.objects.filter(id=cid)
   c.delete()
   return redirect('/viewcart')

def updateqty(request,qv,cid):
  c=Cart.objects.filter(id=cid)
  print(c[0].qty)
  if qv == '1':
    #increase quantity
    t=c[0].qty + 1
    c.update(qty=t)

  else:
    #decrease quantity
    if c[0].qty > 1:
      t=c[0].qty - 1
      c.update(qty=t)
  return redirect('/viewcart')

def placeorder(request):
  #to move product from cart to place order
  userid=request.user.id
  c=Cart.objects.filter(uid=userid)
  # order id
  oid = random.randrange(1000,9999)
  for x in c:
     o=Order.objects.create(order_id=oid, pid=x.pid, uid=x.uid, qty=x.qty)
     o.save()
     x.delete()
  context={}
  orders=Order.objects.filter(uid=request.user.id)
  np=len(orders)
  context['data']=orders
  context['n']=np
  s=0
  for x in orders:
    s= s + x.pid.price * x.qty
  context['total'] =s

  return render(request,'placeorder.html',context)

def makepayment(request):
  orders=Order.objects.filter(uid=request.user.id)
  s=0
  for x in orders:
    s= s+ x.pid.price * x.qty
    oid=x.order_id
  client = razorpay.Client(auth=("rzp_test_cWto9CcftWaLO9", "VuuszHCxUIQkFpil0mgGp6h2"))

  data = { "amount": s * 100, "currency": "INR", "receipt": oid }
  payment = client.order.create(data=data)
  print(payment)
  context ={}
  context['data']=payment

  uemail=request.user.email
  # print(uemail)
  context['uemail']=uemail

  return render(request,'pay.html',context)

def successfully_placed(request):
  return render(request,'successfully_placed.html')

#order place mail sen to customer 
def sendusermail(request,uemail):
  print(uemail)
  msg="Order detail are:---"
  send_mail(
    "E-store order placed successfully",
    msg,
    "patilnikita062@gmail.com"  ,# from owner mail
    [uemail], # to customer mail
    fail_silently=False,
  )
  return redirect("/successfullyplaced")

def contact(request):
  return render(request,'contact.html')

def about(request):
  return render(request,'about.html')
    
   
   