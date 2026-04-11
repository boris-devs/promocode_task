from django.contrib import admin

from promocodes.models import Promocode, PromocodeUsage

admin.site.register(Promocode)
admin.site.register(PromocodeUsage)
