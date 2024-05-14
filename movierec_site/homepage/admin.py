from django.contrib import admin
from .models import Movie, Rating

# Register your models here.

@admin.register(Movie)
class MoviesAdmin(admin.ModelAdmin):
    list_display = ['id','movieId','title']
    list_filter = ['movieId','title']
    search_fields = ['title']
    ordering = ['id','movieId']

@admin.register(Rating)
class MoviesAdmin(admin.ModelAdmin):
    list_display = ['id','user','movie','rating', 'timestamp']
    search_fields = ['user', 'movie']
    date_hierarchy = 'timestamp'
