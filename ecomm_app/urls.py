from django.urls import path
from ecomm_app import views
from django.conf.urls.static import static
from ecomm import settings

urlpatterns = [
    path('',views.home),
    path('pdetail/<pid>',views.product_detail),
    path('viewcart',views.viewcart),
    path('register',views.register),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('catfilter/<cv>',views.catfilter),
    path('sort/<sv>',views.sort),
    path('range',views.range),
    path('addtocart/<pid>',views.addtocart),
    path('remove/<cid>',views.remove),
    path('updateqty/<qv>/<cid>',views.updateqty),
    path('placeorder',views.placeorder),
    path('makepayment',views.makepayment),
    path('sendmail/<uemail>',views.sendusermail),
    path('successfullyplaced',views.successfully_placed),
    path('contact',views.contact),
    path('about',views.about)

]

# only when DBUG = true in setting.py
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)



