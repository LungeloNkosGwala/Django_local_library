from django.urls import path, include
from lmini_app import views

urlpatterns = [
    path("index/",views.index,name='index'),
    path("user_login/",views.user_login, name='user_login'),
    path("register/",views.register,name='register'),
    path("receivestock/",views.receivestock, name = "receivestock"),
    path("loadorder/", views.loadorder, name='loadorder'),
    path("profileupdate/",views.profileupdate, name='profileupdate'),
    path("transaction/",views.inquire_workflow, name="transactions"),
    path("stockonhand/",views.stockonhand_inquire, name = "stockonhand"),
    path("adjustments/", views.adjustments, name = "adjustments"),
    path("purchase/",views.purchase, name = "purchase"),
    path("stockvalue/",views.stockvalue, name='stockvalue'),
    path("createorder/",views.createorder, name="createorder"),
]

