
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from lmini_app.models import Transactions,StockOrder,ProductMaster,Inventory,orderstatus
from django.contrib import messages
from django.db.models import Sum,Aggregate,Q
import pandas as pd
from django import forms
from datetime import datetime


line_status = ['Inactive','New','In Progress','Closed',"Complete"]

# Create your views here.
"""
def my_view(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        print(str(username))
        return username
"""
#@login_required
#def dashboard(request):
 #  return render(request, 'lmini_app/index.html', {"name": request.user.username})

def check_admin(user):
    return user.is_staff


def index(request):
    return render(request,"lmini_app/index.html")

@login_required
@user_passes_test(check_admin,"index")
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request,"lmini_app/index.html")
            #return HttpResponseRedirect(reverse("index"))
            #return redirect("lmini_app/index.html")
    else:
        form = UserCreationForm()
    return render(request, "lmini_app/admin/register.html",{"form":form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                user_d = request.user
                #return HttpResponseRedirect(reverse("index"))
                return render(request,"lmini_app/index.html",{"user_d":user_d})
            else:
                return HttpResponse("Account Not active")
        else:
            print("Somone tried to login and failed")
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request,'lmini_app/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def stockin_tran(request,user_d,partnumber,qty,orderno):
    loadTrans = Transactions.objects.create(partnumber = partnumber)
    loadTrans.type = "stockin"
    loadTrans.qty = qty
    loadTrans.targetqty = qty
    loadTrans.sourcearea = "Purchase"
    loadTrans.targetarea = "stock"
    loadTrans.user_id = str(user_d)
    loadTrans.holdingunit = orderno
    loadTrans.save()

def stockin_stockorder(request,partnumber,orderno,qty):
    qty_s = int(StockOrder.objects.get(partnumber=partnumber, orderno= orderno).qtyreceived)
    StockOrder.objects.filter(partnumber=partnumber, orderno= orderno).update(qtyreceived=int(qty+qty_s), linestatus=line_status[2])

def stockin_inventory_child(request,partnumber,orderno,qty):
    tran_cost = round(qty*float(ProductMaster.objects.get(partnumber=partnumber).costprice),2)
    tran_sale = round(qty*float(ProductMaster.objects.get(partnumber=partnumber).saleprice),2)
    profit = round(float(tran_sale-tran_cost),2)
    Inventory.objects.update_or_create(partnumber=partnumber,packqty=qty,totalcost=tran_cost,totalvalue=tran_sale,profit=profit)

def inventory(request,partnumber,orderno,qty):
    verify = Inventory.objects.filter(partnumber=partnumber).first()
    print(verify)
    if verify is None:
        stockin_inventory_child(request,partnumber,orderno,qty)
    else:
        print("This is wrong")
        qty_s = int(Inventory.objects.get(partnumber=partnumber).packqty)
        qty = qty + qty_s
        Inventory.objects.filter(partnumber = partnumber).delete()
        stockin_inventory_child(request,partnumber,orderno,qty)

def orderstatus_update(request,qty,orderno):
    value_2 = list(StockOrder.objects.filter(orderno=orderno).aggregate(Sum('qtyreceived')).values())[0]
    orderstatus.objects.filter(orderno = orderno).update(qtyreceived = value_2)
    value_3 = StockOrder.objects.filter(orderno=orderno, linestatus = line_status[2]).count()
    orderstatus.objects.filter(orderno = orderno).update(linesreceived = value_3)


@login_required
def receivestock(request):
    user_d = request.user
    avail_order = orderstatus.objects.all().filter(Q(status = line_status[1])|Q(status = line_status[2]))
    if "partnumber" in request.POST and "qty" in request.POST:
        partnumber = request.POST['partnumber']
        qty = int(request.POST['qty'])
        orderno = request.POST['orderno']
        verify = StockOrder.objects.filter(orderno = orderno).first()
        if verify is None:
            print("Please remind Lungelo fix this query")
            messages.warning(request, "This orderno doesn't exist,please request order to be loaded")
            return render(request,"lmini_app/stockin/receivestock.html", {"user_d":user_d,"avail_order":avail_order})
        else:
            verify = ProductMaster.objects.filter(Q(barcode = partnumber)|Q(itemcode = partnumber)|Q(partnumber = partnumber)).first()
            if verify is None:
                print("Part entered doesn't exist on ProductMaster")
                messages.warning(request, "Partnumber entered doesn't exist on ProductMaster")
                return render(request,"lmini_app/stockin/receivestock.html", {"user_d":user_d,"avail_order":avail_order})
            else:
                partnumber = str(ProductMaster.objects.get(Q(barcode = partnumber)|Q(itemcode = partnumber)|Q(partnumber = partnumber)).partnumber)
                verify = StockOrder.objects.filter(orderno=orderno,partnumber=partnumber).first()
                if verify is None:
                    messages.warning(request, "The receiving partnumber is not available on Orderno, please created orderno")
                    return render(request,"lmini_app/stockin/receivestock.html", {"user_d":user_d,"avail_order":avail_order})
                else:
                    if line_status[2] == str(orderstatus.objects.get(orderno=orderno).status):
                        stockin_tran(request,user_d,partnumber,qty,orderno)
                        stockin_stockorder(request,partnumber,orderno,qty)
                        inventory(request,partnumber,orderno,qty)
                        orderstatus_update(request,qty,orderno)
                        print("Stock successfuly")
                        messages.warning(request, "Stock qty successfully received")
                        return render(request,"lmini_app/stockin/receivestock.html", {"user_d":user_d,"avail_order":avail_order})
                    else:
                        messages.warning(request, "Cannot receive on current Order status")
                        return render(request,"lmini_app/stockin/receivestock.html", {"user_d":user_d,"avail_order":avail_order})
    elif "receive_r" in request.POST and "orderno_r" and request.POST:
        orderno_r = request.POST['orderno_r']
        orderstatus.objects.filter(orderno = orderno_r).update(status=line_status[2])
        messages.warning(request, "Order status updated")
        return render(request,"lmini_app/stockin/receivestock.html", {"orderno":orderno_r,"user_d":user_d,"avail_order":avail_order})
    elif "sel_orderno" in request.POST:
        sel_orderno = request.POST['sel_orderno']
        avail_lines = StockOrder.objects.all().filter(orderno = sel_orderno)
        return render(request,"lmini_app/stockin/receivestock.html",{"user_d":user_d,"avail_order":avail_order,"avail_lines":avail_lines})
    else:
        if "close" in request.POST and "sel_close_orderno" in request.POST:
            sel_close_orderno = request.POST['sel_close_orderno']
            print(sel_close_orderno)
            orderstatus.objects.filter(orderno = sel_close_orderno).update(status=line_status[3])
            data = StockOrder.objects.all().filter(orderno = sel_close_orderno)
            for i in data:
                if i.totalqty > i.qtyreceived:
                    StockOrder.objects.filter(orderno = sel_close_orderno, partnumber=i.partnumber).update(qtyshort=int(i.totalqty-i.qtyreceived))
                elif i.totalqty < i.qtyreceived:
                    StockOrder.objects.filter(orderno = sel_close_orderno, partnumber=i.partnumber).update(qtyextra=int(i.qtyreceived- i.totalqty))
                else:
                    pass
            messages.warning(request, "Order status closed successfully")
            return render(request,"lmini_app/stockin/receivestock.html",{"user_d":user_d,"avail_order":avail_order})
    return render(request,"lmini_app/stockin/receivestock.html",{"user_d":user_d,"avail_order":avail_order})

@login_required
@user_passes_test(check_admin,"index")
def loadorder(request):
    user_d = request.user
    if "orderno" in request.POST:
        orderno = str(request.POST['orderno'])

        verify = StockOrder.objects.filter(orderno = orderno).first()
        if verify is None:
            df = pd.read_excel(r"C:\Users\Latitude 7480\Desktop\Data.xlsx", "Sheet1")
            df.orderno= df.orderno.astype(str)
            all_asns = list(df.orderno.unique())
            print(all_asns)
            x = orderno in all_asns
            print(x)
            if x == True:
                df = df[df['orderno']==orderno]
                print(df.orderno[0])
                for i in df.iterrows():
                    LoadAsn = StockOrder.objects.create(orderno = orderno)
                    LoadAsn.partnumber = (str(i[1][2]))
                    LoadAsn.description = (str(i[1][3]))
                    LoadAsn.totalqty = int(i[1][4])
                    LoadAsn.linestatus = line_status[0]
                    LoadAsn.save()
                print("ASN Loaded Successfully")
                messages.success(request, "ASN loaded successfuly")
            else:
                print("Please request ASN")
                messages.success(request, "Please request ASN")
                return render(request,"lmini_app/stockin/loadorder.html")
            return render(request,"lmini_app/stockin/loadorder.html")
        else:
            print("ASN "+orderno+" is already loaded.")
            messages.success(request, "ASN "+orderno+" is already loaded.")
            variable_1 = list(StockOrder.objects.filter(orderno=orderno).aggregate(Sum('totalqty')).values())[0]
            variable_2 = StockOrder.objects.filter(orderno=orderno).count()
            print(str(variable_1), str(variable_2))
            return render(request,"lmini_app/stockin/loadorder.html",{"user_d":user_d})
    else:
        download_orderno(request,user_d)
    form = CsvImportForm()
    #data = {'form':form}
    return render(request,"lmini_app/stockin/loadorder.html",{"form":form,"user_d":user_d})


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(label=".txt File Upload")

@login_required
@user_passes_test(check_admin,"index")
def profileupdate(request):
    user_d = request.user
    if "stock" in request.POST:
        csv_file = request.FILES['csv_upload']

        if not csv_file.name.endswith(".txt"):
            messages.warning(request, "This file is invalid")
            return HttpResponseRedirect(request.path_info)

        file_data = csv_file.read().decode("utf-8")
        csv_data = file_data.split("\n")
        csv_data = csv_data[:-1]

        data = []

        for t in range(6):
            for x in csv_data:
                fields = x.split("\t")
                data.append(fields[t])

        pfep_ls = []
        for i in data:
            line = i.rstrip()
            pfep_ls.append(line)
        

        data = list()
        chunk_size = int(len(pfep_ls)/6)
        for i in range(0, len(pfep_ls), chunk_size):
            data .append(pfep_ls[i:i+chunk_size])


        df = pd.DataFrame(data).transpose()
        df.columns = df.iloc[0]
        df = df[1:]

        for i in df.iterrows():
            ProductMaster.objects.filter(itemcode = i[1][5]).delete()
            ProductMaster.objects.update_or_create(partnumber=i[1][0], productgroup=i[1][1],barcode=str(i[1][2]),costprice=float(i[1][3]), saleprice=float(i[1][4]),itemcode=i[1][5])

        print("ProductMaster successfully updated")
        messages.warning(request, "ProductMaster successfully updated")
    

    form = CsvImportForm()
    #data = {'form':form}

    return render(request,"lmini_app/admin/profileupdate.html",{'form':form,"user_d":user_d})



def download_orderno(request,user_d):
    if "download_orderno" in request.POST:
        csv_file = request.FILES['csv_upload']

        if not csv_file.name.endswith(".txt"):
            messages.warning(request, "This file is invalid")
            return HttpResponseRedirect(request.path_info)

        file_data = csv_file.read().decode("utf-8")
        csv_data = file_data.split("\n")
        csv_data = csv_data[:-1]

        data = []

        for t in range(5):
            for x in csv_data:
                fields = x.split("\t")
                data.append(fields[t])

        pfep_ls = []
        for i in data:
            line = i.rstrip()
            pfep_ls.append(line)
        

        data = list()
        chunk_size = int(len(pfep_ls)/5)
        for i in range(0, len(pfep_ls), chunk_size):
            data .append(pfep_ls[i:i+chunk_size])


        df = pd.DataFrame(data).transpose()
        df.columns = df.iloc[0]
        df = df[1:]

     

        df.dropna(inplace = True)
        df = df[df.qty != '']
        df['qty'] = df['qty'].astype('int')
        tot_qty = df['qty'].sum()

        print(df)

        orderno_r = df.iloc[0].tolist()[0]
        
        verify = StockOrder.objects.filter(orderno=orderno_r).first()
        if verify is None:
            for i in df.iterrows():
                print(i[1][4])
                StockOrder.objects.update_or_create(orderno=i[1][0], partnumber=i[1][2],totalqty=i[1][4], line_status=line_status[0])
            loadorderstatus = orderstatus.objects.create(orderno = orderno_r)
            loadorderstatus.status = line_status[1]
            loadorderstatus.nooflines = df.iloc[:, 5-1:5].count()
            loadorderstatus.totalqty = tot_qty
            loadorderstatus.save()
            print("Stockorder successfully updated")
            messages.warning(request, "Stockorder successfully updated")

        else:
            print("Stockorder no already exist")
            messages.warning(request, "Stockorder no already exist")


    form = CsvImportForm()
    #data = {'form':form}

    return render(request,"lmini_app/stockin/loadorder.html",{'form':form,"user_d":user_d})

@login_required
@user_passes_test(check_admin,"index")
def inquire_workflow(request):
    user_d = request.user
    query = request.GET.get('search')
    sd = request.GET.get("from")
    ed = request.GET.get("to")
    
    if ed == "" and sd == "":
        ed = "2060-12-31"
        sd = "2020-12-31"
    elif ed == "":
        ed = "2060-12-31"
    elif sd == "":
        sd = "2020-12-31"
    else:
        pass


    verify = ProductMaster.objects.filter(Q(partnumber=query)|Q(barcode=query)|Q(itemcode=query)).first()
    if verify is None:
        verify = Transactions.objects.filter(Q(holdingunit=query)|Q(type=query))
        if verify is None:
            return render(request,"lmini_app/inquire/transactions.html",{"user_d":user_d})
        else:
            data = Transactions.objects.all().filter(Q(holdingunit=query)|Q(type=query), transactiondate__range=[sd, ed])
            return render(request,"lmini_app/inquire/transactions.html",{"data":data,"user_d":user_d})
    else:
        partnumber = str(ProductMaster.objects.get(Q(partnumber=query)|Q(barcode=query)|Q(itemcode=query)).partnumber)
        data = Transactions.objects.all().filter(partnumber=partnumber,transactiondate__range=[sd, ed])
        return render(request,"lmini_app/inquire/transactions.html",{"data":data,"user_d":user_d})
    
    return render(request,"lmini_app/inquire/transactions.html")

@login_required
@user_passes_test(check_admin,"index")
def stockonhand_inquire(request):
    user_d = request.user
    data = ProductMaster.objects.all()
    if "partnumber" in request.GET:
        query = request.GET.get('partnumber')
        verify = ProductMaster.objects.filter(Q(partnumber=query)|Q(barcode=query)|Q(itemcode=query)).first()
        if verify is None:
            return render(request,"lmini_app/inquire/stockonhand.html",{"data":data,"user_d":user_d})
        else:
            partnumber = str(ProductMaster.objects.get(Q(partnumber=query)|Q(barcode=query)|Q(itemcode=query)).partnumber)
            data = ProductMaster.objects.all().filter(partnumber = partnumber)
            inventory = Inventory.objects.all().filter(partnumber=partnumber)
            return render(request,"lmini_app/inquire/stockonhand.html",{"data":data,"inventory":inventory,"user_d":user_d})
    else:
        return render(request,"lmini_app/inquire/stockonhand.html",{"data":data,"user_d":user_d})

def adjust_tran(request,user_d,partnumber,qty):
    s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
    loadTrans = Transactions.objects.create(partnumber = partnumber)
    loadTrans.type = "adjustment"
    loadTrans.sourceqty = s_qty - (qty)
    loadTrans.qty = qty
    loadTrans.targetqty = s_qty
    loadTrans.sourcearea = "stock"
    loadTrans.targetarea = "stock"
    loadTrans.user_id = str(user_d)
    loadTrans.save()

@login_required
@user_passes_test(check_admin,"index")
def adjustments(request):
    user_d = request.user
    orderno = ""
    if "adjust" in request.POST and "up" in request.POST:
        qty = int(request.POST['qty'])
        partnumber = request.POST['partnumber']
        adjust = request.POST['up']
        if adjust == 'up':
            verify = ProductMaster.objects.filter(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).first()
            if verify is None:
                print("Part number doesn't exist on ProductMaster")
                messages.warning(request, "Partnumber doesn't exist on ProductMaster")
                return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})
            else:
                partnumber = str(ProductMaster.objects.get(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).partnumber)
                inventory(request,partnumber,orderno,qty)
                adjust_tran(request,user_d,partnumber,qty)
                print("Successfully adjusted Partnumber")
                messages.warning(request, "Successfully adjusted Partnumber")
                return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})
        else:
            qty = qty*-1
            verify = ProductMaster.objects.filter(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).first()
            if verify is None:
                return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})
            else:
                partnumber = str(ProductMaster.objects.get(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).partnumber)
                s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
                if s_qty < qty:
                    print("Cannot down adjustment ")
                    messages.warning(request, "Cannot down adjustment more available qty")
                    return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})
                else:
                    inventory(request,partnumber,orderno,qty)
                    adjust_tran(request,user_d,partnumber,qty)
                    s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
                    if s_qty == 0:
                        Inventory.objects.filter(partnumber=partnumber).delete()
                    else:
                        pass
                    print("Successfully adjusted Partnumber")
                    messages.warning(request, "Successfully adjusted Partnumber")
                    return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})
    return render(request,"lmini_app/admin/adjustments.html",{"user_d":user_d})

def purchase_tran(request,user_d,partnumber,qty):
    s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
    loadTrans = Transactions.objects.create(partnumber = partnumber)
    loadTrans.type = "stockout"
    loadTrans.sourceqty = s_qty - (qty)
    loadTrans.qty = qty
    loadTrans.targetqty = s_qty
    loadTrans.sourcearea = "stock"
    loadTrans.targetarea = "purchase_order"
    loadTrans.user_id = str(user_d)
    loadTrans.save()

@login_required
def purchase(request):
    user_d = request.user
    orderno = ""
    if request.method == "POST":
        partnumber = request.POST['partnumber']
        qty = int(request.POST['qty'])
        verify = ProductMaster.objects.filter(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).first()
        if verify is None:
            print("Partnumber doesn't exist on the system")
            messages.warning(request, "Partnumber doesn't exist in ProductMaster")
            return render(request,"lmini_app/stockout/purchase.html",{"user_d":user_d})
        else:
            partnumber = str(ProductMaster.objects.get(Q(partnumber=partnumber)|Q(barcode=partnumber)|Q(itemcode=partnumber)).partnumber)
            verify = Inventory.objects.filter(partnumber=partnumber).first()
            if verify is None:
                print("Out of stock")
                messages.warning(request, "No stock available for this Product")
                return render(request,"lmini_app/stockout/purchase.html",{"user_d":user_d})
            else:
                s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
                if s_qty < qty:
                    print("Unable to process purchase, The qty is more than available stock")
                    messages.warning(request, "Unable to process purchase, The qty is more than available stock")
                    return render(request,"lmini_app/stockout/purchase.html",{"user_d":user_d})
                else:
                    qty = qty*-1
                    inventory(request,partnumber,orderno,qty)
                    purchase_tran(request,user_d,partnumber,qty)
                    s_qty = int(Inventory.objects.get(partnumber=partnumber).packqty)
                    if s_qty == 0:
                        Inventory.objects.filter(partnumber=partnumber).delete()
                    else:
                        pass
                    print("Successfully purchased part")
                    messages.warning(request, "Successfully purchased part")
                    return render(request,"lmini_app/stockout/purchase.html",{"user_d":user_d})
    return render(request,"lmini_app/stockout/purchase.html",{"user_d":user_d})


@login_required
@user_passes_test(check_admin,"index")
def stockvalue(request):
    user_d = request.user
    curr_value = list(Inventory.objects.filter().aggregate(Sum('totalvalue')).values())[0]
    curr_profit = list(Inventory.objects.filter().aggregate(Sum('profit')).values())[0]
    if "search" in request.GET:
        print("Request Through")
        tran_type = []
        amount = []
        part = []
        totalcost = []
        totalvalue = []
        sd = request.GET.get("from")
        ed = request.GET.get("to")
        
        if ed == "" and sd == "":
            ed = "2060-12-31"
            sd = "2020-12-21"
        elif ed == "":
            ed = "2060-12-31"
        elif sd == "":
            sd = "2020-12-31"
        else:
            pass

        data = Transactions.objects.all().filter(transactiondate__range=[sd, ed]).values()

        sd = str(sd)
        ed = str(ed)

        for i in data:

            tran_type.append(i.get("type"))
            part.append(i.get("partnumber"))
            amount.append(i.get("qty"))
            totalcost.append(float(ProductMaster.objects.get(partnumber=i.get("partnumber")).costprice)*int(i.get("qty")))
            totalvalue.append(float(ProductMaster.objects.get(partnumber=i.get("partnumber")).saleprice)*int(i.get("qty")))
        columns=['tran_type','part','amount',"totalcost","totalvalue"]
        lists = [tran_type,part,amount,totalcost,totalvalue]
        df = pd.concat([pd.Series(x) for x in lists], axis=1)
        df.columns  = columns
        

        sales = round(df[df['tran_type']=="stockout"]['totalvalue'].sum()*-1,1)
        adjustments = round(df[df['tran_type']=="adjustment"]['totalvalue'].sum(),1)
        profit = round(sales - round(df[df['tran_type']=="stockout"]['totalcost'].sum()*-1,1),1)
        return render(request, "lmini_app/inquire/stockvalue.html",{"user_d":user_d,"sales":sales,"adjustments":adjustments,"curr_value":curr_value,"curr_profit":curr_profit,"profit":profit,"sd":sd,"ed":ed})
    return render(request, "lmini_app/inquire/stockvalue.html",{"user_d":user_d,"curr_value":curr_value,"curr_profit":curr_profit})
        
