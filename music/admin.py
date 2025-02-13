from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(neutral)
admin.site.register(happy)
admin.site.register(sad)
admin.site.register(fear)
admin.site.register(surprise)
admin.site.register(angry)