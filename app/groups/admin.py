from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    def updated_at_verbose(self, obj):
        return obj.updated_at.strftime("%d %b %Y %H:%M:%S")
    updated_at_verbose.admin_order_field = 'updated_at'
    updated_at_verbose.short_description = 'Verbose updated at'

    date_hierarchy = 'updated_at'
    list_display = ('id', 'group_id', 'title', 'updated_at_verbose')
