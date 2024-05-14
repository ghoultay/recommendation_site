from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Movie(models.Model):
    imdb_id = models.CharField(max_length=10,unique = True, blank=False)
    second_id = models.IntegerField(unique = True, blank=False)
    movieId = models.IntegerField(unique = True, blank=False)
    adult = models.BooleanField(null=False, blank=True)
    title = models.CharField(max_length=50, blank=False)
    belongs_to_collection = models.JSONField(null=False, blank=True)
    budget = models.IntegerField(null=False, blank=True)
    homepage = models.CharField(null=False, blank=True, max_length=200)
    original_language = models.CharField(null=False, blank=True, max_length=5)
    original_title = models.CharField(null=False, blank=True, max_length=50)
    overview = models.CharField(null=False, blank=True, max_length=900)
    popularity = models.FloatField(null=False, blank=True)
    poster_path = models.CharField(null=False, blank=True, max_length=100)
    production_companies = models.JSONField(null=False, blank=True)
    production_countries = models.JSONField(null=False, blank=True)
    release_date = models.DateField(null=False, blank=True)
    year = models.SmallIntegerField(null=False, blank=True)
    revenue = models.FloatField(null=False, blank=True)
    runtime = models.FloatField(null=False, blank=True)
    spoken_languages = models.JSONField(null=False, blank=True)
    status = models.CharField(null=False, blank=True, max_length=15)
    tagline = models.CharField(null=False, blank=True, max_length=900)
    video = models.BooleanField(null=False, blank=True)
    vote_average = models.FloatField(null=False, blank=True)
    vote_count = models.FloatField(null=False, blank=True)
    cast = models.JSONField(null=False, blank=True)
    crew = models.JSONField(null=False, blank=True)
    keywords = models.JSONField(null=False, blank=True)
    cast_size = models.SmallIntegerField(null=False, blank=True)
    crew_size = models.SmallIntegerField(null=False, blank=True)
    genres = models.JSONField(null=False, blank=True)
    director = models.CharField(null=False, blank=True, max_length=50)
    actors = models.JSONField(null=False, blank=True)

    

    def __str__(self):
        return self.title
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=False)
    rating = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return  f"Rating for {self.movie.title} by {self.user.username}"
    
    class Meta:
        # Ensures each user can only rate each movie once
        unique_together = (('user', 'movie'),)
