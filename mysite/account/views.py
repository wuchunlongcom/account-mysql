# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse,\
    StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from monthdelta import monthdelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Company, Material, Order
from django.contrib.auth.models import User, Group
import datetime
import os
import re
import tempfile
import uuid
import xlsxwriter
from myAPI.download import downLoadFile
from myAPI.pageAPI import djangoPage,PAGE_NUM,toInt
from myAPI.fileAPI import ListToXlsx
from myAPI.searchAPI import SearchNameContact

def _getOperators():
    operators = Group.objects.get(name='Operator').user_set.all()
    return [user for user in User.objects.all() if user.is_superuser or user in operators]

@login_required
def customer(request, page): 
    operators = _getOperators()
    
    if request.user not in operators:
        return HttpResponseRedirect('/')
         
    cleanData = request.GET.dict()     
    companys = SearchNameContact(Company, cleanData.get('name',''),cleanData.get('contact',''))
    companys = companys.order_by('-id')
    company_list, pageList, num_pages, page = djangoPage(companys,page,PAGE_NUM)  #调用分页函数
    offset = PAGE_NUM * (page - 1)
    return render(request, 'account/customer.html', context=locals())

def _Order(cleanData):
    orders = Order.objects
    operators = _getOperators()
    
    if request.user not in operators:
        orders = orders.filter(company__username=request.user)
    elif cleanData.get('company', ''):
        orders = orders.filter(company__name__icontains=cleanData['company'])
        
    if cleanData.get('content', ''):
        orders = orders.filter(content__icontains=cleanData['content'])
    
    if cleanData.get('author', ''):
        orders = orders.filter(author__username=cleanData['author'])
        
    if cleanData.get('checkout', '') == 'on' and cleanData.get('non_checkout', '') == 'on':
        orders = orders
    elif cleanData.get('checkout', '') == 'on':
        orders = orders.filter(checkout=True)
    elif cleanData.get('non_checkout', '') == 'on':
        orders = orders.filter(checkout=False)
    
    monthNum = cleanData.get('month', '1')
    try:
        monthNum = int(monthNum)
    except Exception as _e:
        monthNum = 1
    if monthNum > 0:
        endDate = datetime.date.today()
        startDate = endDate - monthdelta(monthNum)
        orders = orders.filter(date__range=[startDate, endDate])
    return orders, monthNum

def _filterOrder(request, cleanData):
    orders = Order.objects
    operators = _getOperators()
    
    if request.user not in operators:
        orders = orders.filter(company__username=request.user)
    elif cleanData.get('company', ''):
        orders = orders.filter(company__name__icontains=cleanData['company'])
        
    if cleanData.get('content', ''):
        orders = orders.filter(content__icontains=cleanData['content'])
    
    if cleanData.get('author', ''):
        orders = orders.filter(author__username=cleanData['author'])
        
    if cleanData.get('checkout', '') == 'on' and cleanData.get('non_checkout', '') == 'on':
        orders = orders
    elif cleanData.get('checkout', '') == 'on':
        orders = orders.filter(checkout=True)
    elif cleanData.get('non_checkout', '') == 'on':
        orders = orders.filter(checkout=False)
    
    monthNum = cleanData.get('month', '1')
    try:
        monthNum = int(monthNum)
    except Exception as _e:
        monthNum = 1
    if monthNum > 0:
        endDate = datetime.date.today()
        startDate = endDate - monthdelta(monthNum)
        orders = orders.filter(date__range=[startDate, endDate])
    return orders, monthNum

# http://localhost:8000/account/billing/
@login_required
def billing(request, page):
    operators = _getOperators()     
    cleanData = request.GET.dict()
    queryString = '?'+'&'.join(['%s=%s' % (k,v) for k,v in cleanData.items()])
    orders, monthNum = _filterOrder(request, cleanData)
      
    TotalTax = sum(orders.values_list('priceIncludeTax', flat=True))
    orders = orders.order_by('-date', '-id')    
    if request.user in operators: #如果登录用户在Operator组
        company_name_list = Company.objects.values_list('name', flat=True) 
        type_list = [i[0] for i in Order.ORDER_TYPE]
        material_name_list = Material.objects.values_list('name', flat=True)
        taxPercent_list = [i[0] for i in Order.ORDER_TAX]   
    order_list, pageList, num_pages, page = djangoPage(orders,page,PAGE_NUM)  #调用分页函数
    offset = PAGE_NUM * (page - 1)
    return render(request, 'account/billing.html', context=locals())

@login_required
def addBilling(request):
    operators = _getOperators()

    if request.user not in operators or request.method != 'POST':
        return HttpResponseRedirect('/')
    
    cleanData = request.POST.dict()
    company = Company.objects.get(name=cleanData['company'])
    type = cleanData.get('type', '')
    if type not in [i[0] for i in Order.ORDER_TYPE]:
        type = 'Design'
    if type in ['Design', 'Other']:
        price = float(cleanData.get('price', ''))
    count = float(cleanData.get('count', '1'))
    taxPercent = cleanData.get('taxPercent', Order.ORDER_TAX[0][0])
    taxPercent = int(taxPercent)
    if taxPercent not in [int(i[0]) for i in Order.ORDER_TAX]:
        taxPercent = Order.ORDER_TAX[0][0]
    taxPercent = int(taxPercent)
     
    o = Order()
    o.company = company
    o.type = type
    o.content = cleanData.get('content', '')
     
    reCmp = re.compile('(\d+(\.\d+)?)')
    if type == 'Manufacture':
        material = Material.objects.get(name=cleanData['material'])
        o.material = material
         
        try:
            sizeHeight = reCmp.search(cleanData.get('sizeHeight', ''))
            sizeHeight = float(sizeHeight.groups()[0])
        except Exception as _e:
            sizeHeight = 1
        o.sizeHeight = sizeHeight
         
        try:
            sizeWidth = reCmp.search(cleanData.get('sizeWidth', ''))
            sizeWidth = float(sizeWidth.groups()[0])
        except Exception as _e:
            sizeWidth = 1
        o.sizeWidth = sizeWidth
         
        o.price = sizeHeight * sizeWidth * material.price
    else:
        o.price = price

    o.author = request.user
    o.quantity = count
    o.taxPercent = taxPercent
    o._autoFill()
    o.save()
      
    return HttpResponseRedirect('/account/billing/')

@login_required
def addCustomer(request):
    operators = _getOperators()
    
    if request.user not in operators or request.method != 'POST':
        return HttpResponseRedirect('/')
    cleanData = request.POST.dict()    
    customerGroup = Group.objects.get(name='Customer')
    
    id = User.objects.all().last().id + 1
    username = 'cx%06d' % id
    user = User.objects.create_user(username=username, password='1234qazx')
    user.is_staff = True
    user.is_superuser = False
    user.groups.add(customerGroup)
    user.save()  
    user = User.objects.get(username=username)
    
    c = Company()
    c.name = cleanData['name']
    c.taxNumber = cleanData['tax_number']
    c.address = cleanData['address']
    c.bank = cleanData['bank']
    c.bankAccount = cleanData['account']
    c.contact = cleanData['contact']
    c.telephone = cleanData['telephone']
    c.username = user
    c.save()
    
    return HttpResponseRedirect('/account/customer/')

def ModelToList(order_list):
    try: 
        ids = [i.id for i in order_list ]
        authors = [i.author.username for i in order_list ]
 
        dates = [str(i.date) for i in order_list]
         
        names = [i.company.name for i in order_list]    
        types = [u'制作' if i.type == 'Manufacture' else i.type for i in order_list ]
        contents = [i.content for i in order_list ]
        materials = ['-' if i.type != 'Manufacture' else \
                     str(i.material).decode('UTF-8') + ' (' +str(i.priceMaterial) + \
                     ' * '+str(i.sizeHeight) + ' * '+str(i.sizeWidth) + ')'  for i in order_list ]            
        prices = [i.price for i in order_list ]
        quantitys = [i.quantity for i in order_list ]
        taxPercents = [i.taxPercent for i in order_list ]
        priceIncludeTaxs = [i.priceIncludeTax for i in order_list ]
        checkouts = [u'已完成' if i.checkout else u'未结算' for i in order_list ]
        return [ids, authors, dates, names, types, contents, materials, \
            prices, quantitys, taxPercents, priceIncludeTaxs, checkouts, ] 
    except Exception as _e:       
        return []   

def convertxlsx(order_list, filePath):    
    headings = ['ID',u'记录人',u'日期',u'公司',u'类型',u'内容',u'材料',\
                u'单价',u'数量',u'税率',u'含税价',u'结算']
    data_list = ModelToList(order_list)
    return ListToXlsx(data_list, headings, filePath)

@login_required
def makexlsx(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/')
    
    cleanData = request.POST.dict()
    orders, _monthNum = _filterOrder(request, cleanData)
    order_list = orders.order_by('-date','-id')

    downFilePath = r'Orders-%s.xlsx' % (datetime.datetime.now().strftime('%Y%m%d'),)
    tempDir = tempfile.mkdtemp() 
    tempFilePath = os.path.join(tempDir, '%s.xlsx' % uuid.uuid4().hex)    
    if convertxlsx(order_list, tempFilePath):           
        return downLoadFile(tempFilePath,downFilePath)
       
    return HttpResponseRedirect(r'/account/billing/')



   