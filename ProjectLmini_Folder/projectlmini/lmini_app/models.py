from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class Transactions(models.Model):
    type = models.CharField(max_length=30)
    orderno = models.CharField(max_length=30)
    partnumber = models.CharField(max_length=30)
    sourceqty = models.IntegerField(default=0)
    qty = models.IntegerField(default=0)
    targetqty = models.IntegerField(default=0)
    sourcearea = models.CharField(max_length=30)
    targetarea = models.CharField(max_length=30)
    holdingunit = models.CharField(max_length=30)
    transactiondate = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=30)


class ProductMaster(models.Model):
    itemcode = models.CharField(max_length=30)
    partnumber = models.CharField(max_length=30)
    productgroup = models.CharField(max_length=30)
    barcode = models.CharField(max_length=30)
    costprice = models.FloatField(default = 0)
    saleprice = models.FloatField(default = 0)


class StockOrder(models.Model):
    orderno = models.CharField(max_length=30)
    partnumber = models.CharField(max_length=30)
    description = models.CharField(default="Inactive",max_length=128)
    totalqty = models.IntegerField(default = 0)
    qtyreceived = models.IntegerField(default = 0)
    qtyshort = models.IntegerField(default = 0)
    qtyextra = models.IntegerField(default = 0)
    qtydamanged = models.IntegerField(default = 0)
    linestatus = models.CharField(max_length = 30)

class Inventory(models.Model):
    partnumber = models.CharField(max_length=30)
    description = models.CharField(max_length=128)
    packqty = models.IntegerField(default = 0)
    pendingqty = models.IntegerField(default = 0)
    totalcost = models.FloatField(default = 0)
    totalvalue = models.FloatField(default = 0)
    profit = models.FloatField(default = 0)

class orderstatus(models.Model):
    orderno = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    nooflines = models.IntegerField(default = 0)
    linesreceived = models.IntegerField(default = 0)
    totalqty = models.IntegerField(default = 0)
    qtyreceived = models.IntegerField(default = 0)
    createdate = models.DateTimeField(auto_now_add=True)
    closeddate = models.DateTimeField(null=True, blank=True)

    




