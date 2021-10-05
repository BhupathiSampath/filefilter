from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from split.models import tsvfile
# Register your models here.
# class tsvfile(tsvfile):
#     list_display = ('index', 'strain','lineage','mutation_deletion')
#     search_fields = ('strain','lineage','mutation_deletion')
#     # readonly_fields = ('date_joined','last_login')

#     filter_horizontal = ()
#     list_filter = ()
#     fieldsets = ()

admin.site.register(tsvfile)