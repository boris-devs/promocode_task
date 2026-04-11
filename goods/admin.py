from django.contrib import admin

from goods.models import Category, Good

admin.site.register(Good)
admin.site.register(Category)
