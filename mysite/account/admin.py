# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Company, Material, Order


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'taxNumber', 'address', 'bank', 'bankAccount',
                    'contact', 'username', 'telephone')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('company', 'date', 'type', 'content', 'material',
                    'sizeWidth', 'sizeHeight', 'priceMaterial', 'price',
                    'quantity', 'priceTotal', 'taxPercent', 'priceIncludeTax',
                    'checkout', 'author',)
    list_editable = ['checkout', ]

admin.site.register(Material, MaterialAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Order, OrderAdmin)

"""
from .models import  Blog, Author, Entry
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):    
    list_display = ('id','name','tagline')
    
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):    
    list_display = ('id','name','email')
    
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):    
    list_display = ('id','blog','headline','body_text','author_list')
    def author_list(self, entry):
        '''多对多字段'''
        return ','.join([i.name for i in entry.author.all()])
        #names = map(lambda x: x.name, entry.author.all())
        #return ', '.join(names)
        
"""