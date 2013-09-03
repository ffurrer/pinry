from django.contrib import admin
from pinry.core.models import LightBox

class LightBoxAdmin(admin.ModelAdmin):
    pass
admin.site.register(LightBox, LightBoxAdmin)