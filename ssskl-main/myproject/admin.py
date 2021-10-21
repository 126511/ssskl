from django.contrib import admin
from myproject.models import *
from django.contrib.admin import SimpleListFilter

admin.site.register(Profile)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(Prepaid)
admin.site.register(Badge)
admin.site.register(User_badge)