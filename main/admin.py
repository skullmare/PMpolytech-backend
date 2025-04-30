from django.contrib import admin
from .models import News
# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'created_at')
    list_filter = ('pub_date',)
    search_fields = ('title', 'content')
    date_hierarchy = 'pub_date'