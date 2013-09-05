from django.contrib import admin
from pinry.core.models import LightBox, Image

class LightBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'admin_image')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin_image', 'image')


admin.site.register(LightBox, LightBoxAdmin)
admin.site.register(Image, ImageAdmin)