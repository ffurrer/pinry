from django.contrib import admin
from pinry.core.models import LightBox, Image, Pin

class LightBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'admin_image', 'exclude')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin_image', 'image')


class PinAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin_image', 'submitter')


admin.site.register(LightBox, LightBoxAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Pin, PinAdmin)