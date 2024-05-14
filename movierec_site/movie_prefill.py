from django.utils.dateparse import parse_date
import os
import django
import csv
from tqdm import tqdm

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movierec_site.settings')
django.setup()
from homepage.models import Movie

if __name__ == "__main__":
    with open("dataset\my_movies.csv", "r", encoding="utf-8") as source:
        lines = len(source.readlines())
    
    with open("dataset\my_movies.csv", "r", encoding="utf-8") as source:
        csv_reader = csv.reader(source)
        # Skip header if it exists
        next(csv_reader, None)
        for row in tqdm(csv_reader, total=lines):
            # Assuming your someGenerator function yields tuples with movie data
            imdb_id, second_id, movieId, adult, title, belongs_to_collection, budget, homepage, original_language, original_title, overview, popularity, poster_path, production_companies, production_countries, release_date, year, revenue, runtime, spoken_languages, status, tagline, video, vote_average, vote_count, cast, crew, keywords, cast_size, crew_size, genres, director, actors = row
            # Convert release_date string to DateField
            release_date = parse_date(release_date)

            # Create Movie object and save it
            movie = Movie.objects.create(
                imdb_id=imdb_id,
                second_id=second_id,
                movieId=movieId,
                adult=adult,
                title=title,
                belongs_to_collection=belongs_to_collection,
                budget=budget,
                homepage=homepage,
                original_language=original_language,
                original_title=original_title,
                overview=overview,
                popularity=popularity,
                poster_path=poster_path,
                production_companies=production_companies,
                production_countries=production_countries,
                release_date=release_date,
                year=year,
                revenue=revenue,
                runtime=runtime,
                spoken_languages=spoken_languages,
                status=status,
                tagline=tagline,
                video=video,
                vote_average=vote_average,
                vote_count=vote_count,
                cast=cast,
                crew=crew,
                keywords=keywords,
                cast_size=cast_size,
                crew_size=crew_size,
                genres=genres,
                director=director,
                actors=actors
            )
            movie.save()
    print('Success!!!')
