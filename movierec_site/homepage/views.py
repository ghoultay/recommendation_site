from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Max
from .forms import RegisterForm
from .models import Rating, Movie, User
from implicit.nearest_neighbours import BM25Recommender
from implicit.als import AlternatingLeastSquares
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

model = BM25Recommender(K=30, K1=1, B=0.2)
smd = pd.read_csv("./movierec_site/homepage/dataset/my_movies.csv")
als = AlternatingLeastSquares(**{'factors': 50, 'regularization': 1.0, 'iterations': 30, 'alpha': 0.1, 'random_state': 42})
model = model.load("./movierec_site/homepage/models_data/model_implicit.npz")
als = als.load("./movierec_site/homepage/models_data/als_model.npz")

# Create your views here.
def unit_vector_normalize(arr):
    norm = np.linalg.norm(arr)
    return arr / norm

def improved_recommendations_by_idx_v2(idx):
    if type(idx) != list():
        idx = [idx-1]
        
    movie_indices_knn, knn_scores = model.similar_items(idx, N=30)
    knn_scores = unit_vector_normalize(knn_scores.flatten())[1:]
    movie_indices_knn = movie_indices_knn.flatten()[1:]
    
    movie_indices_als, als_scores = als.similar_items(idx, N=30)
    als_scores = unit_vector_normalize(als_scores.flatten())[1:]
    movie_indices_als = movie_indices_als.flatten()[1:]
    
    df1 = pd.DataFrame({'idx': movie_indices_knn, 'model_score1': knn_scores})
    df2 = pd.DataFrame({'idx': movie_indices_als, 'model_score2': als_scores})
    
    # Merge the dataframes on the 'idx' column with a left join
    merged_df = pd.merge(df1, df2, on='idx', how='outer')
    
    del df1, df2
    #print(merged_df)
    # Fill missing values with zeros
    merged_df.fillna(0, inplace=True)

    # Define the weights
    weight1 = 0.4
    weight2 = 0.6
    
     # Calculate the combined score with popularity penalty
    merged_df['popularity'] = smd['popularity'].iloc[merged_df['idx'].values].values
    
    # Calculate the combined score
    merged_df['combined_score'] = weight1 * merged_df['model_score1'] + weight2 * merged_df['model_score2']

    # Apply XQuAD re-ranking
    def xquad_re_rank(df, num_recommendations=20, lambda_diversity=0.6):
        selected_indices = []
        aspect_coverage = np.zeros(len(df))
        
        for _ in range(num_recommendations):
            best_candidate = None
            best_score = -np.inf
            
            for idx in df.index:
                if idx in selected_indices:
                    continue
                
                candidate_score = df.loc[idx, 'model_score2']
                diversity_score = -lambda_diversity * aspect_coverage[idx]
                total_score = candidate_score + diversity_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_candidate = idx
            
            if best_candidate is not None:
                selected_indices.append(best_candidate)
                aspect_coverage += df.loc[best_candidate, 'model_score2']
        
        return df.loc[selected_indices]

    # Re-rank the merged_df with XQuAD
    re_ranked_df = xquad_re_rank(merged_df, num_recommendations=20, lambda_diversity=0.5)
    re_ranked_df['combined_score'] = weight1 * merged_df['model_score1'] + weight2 * merged_df['model_score2']

    re_ranked_df = re_ranked_df.head(15) 
    re_ranked_df['title'] = re_ranked_df['idx'].apply(lambda x: Movie.objects.get(id=x+1).title)
    re_ranked_df.drop(['combined_score', 'model_score1', 'model_score2'], axis=1, inplace=True)
    dict_of_recs = re_ranked_df.to_dict(orient='list')

    return dict_of_recs


def create_csr_matrix_for_user(user_id):
    user_ratings = Rating.objects.filter(user=user_id)

    user_movie_ratings = [(rating.movie_id, rating.rating) for rating in user_ratings]
    max_movie_id = Rating.objects.aggregate(Max('movie_id'))['movie_id__max']
    movie_ids, ratings = zip(*user_movie_ratings)
    
    user_matrix = csr_matrix((ratings, (np.zeros_like(movie_ids), movie_ids)), shape=(1, max_movie_id + 1))
    
    return user_matrix


def index(request):    

    if request.GET.get('film_suggestion'):
        valname = request.GET.get('film_suggestion')
        #get equivalent url from model
        movie_data = Movie.objects.filter(title=valname).values("title","id")[0]
        # loading model
        dict_of_recs = improved_recommendations_by_idx_v2(movie_data["id"])
        dict_of_recs = [[idx+1, title] for idx, title in zip(dict_of_recs['idx'], dict_of_recs['title'])]
        return render(request, "homepage/home.html", {'form_submitted': True, 'movie_card': dict_of_recs})
    return render(request, "homepage/home.html", {})

def search_film(request):
    """everytime user inputs to search box, this function runs"""
    name = request.GET.get("name")
    namelist = []
    if name:
        #collect every objects that contains the input text
        movie_objects = Movie.objects.filter(title__icontains=name)
        for movie in movie_objects:
            namelist.append((movie.title, movie.vote_average))
        namelist.sort(key=lambda a: a[1], reverse=True)
        namelist = [i for i,j in namelist[:5]]
    return JsonResponse({'status':200, 'name':namelist})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return redirect("profile")
    else:
        form = RegisterForm()
    return render(request, "homepage/register.html", {"form": form})

def films(request): 

    # Query all movies from the database
    if request.GET.get('valname'): 
            #if valname sent get the name
            valname = request.GET.get('valname')
            #get equivalent url from model
            movie_data = Movie.objects.filter(title=valname).values("title","id")[0]
            return JsonResponse({'title': movie_data["title"], 'id': movie_data["id"]},status=200) #return json response
    
    if request.POST.get('valname'):
        valname = request.GET.get('valname')
        #get equivalent url from model
        movie_data = Movie.objects.filter(title=valname).values("title","id")[0]
        print(movie_data["title"])
        return JsonResponse({'title': movie_data["title"], 'id': movie_data["id"]},status=200) #return json response
    
    movies_list = Movie.objects.all()
    paginator = Paginator(movies_list, 30)
    page_number = request.GET.get('page',1)
    movies = paginator.get_page(page_number)

    return render(request, "homepage/films.html", {"movies": movies})

def film_detail(request, id):

    def generate_star_counts(rating):
        # Split the rating into integer and decimal parts
        rating = round(rating * 2) / 4
        integer_part, decimal_part = divmod(rating, 1)

        # Determine the number of full, half, and empty stars
        full_stars = int(integer_part)
        half_star = 1 if decimal_part >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star

        # Return the list representing the star counts
        return [full_stars, half_star, empty_stars]
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            val = request.POST.get('val')
            user_instance = User.objects.get(pk=request.user.id)
            movie_instance = Movie.objects.get(pk=id)
            Rating.objects.update_or_create(user=user_instance, movie=movie_instance, defaults={'rating': val})

            user_matrix = create_csr_matrix_for_user(user_instance.id)
            als.partial_fit_users([162542+user_instance.id], user_matrix)
            als.save('homepage/models_data/als_model.npz')

            return JsonResponse({'success':'true', 'score': val}, safe=False)    
        
        else:
            return JsonResponse({'error': 'true'}, status=403)
    else:
        # Retrieve the movie object using the provided id
        movie = get_object_or_404(Movie, pk=id)
    
        # Render the movie detail template with the movie object
        return render(request, 'homepage/film_detail.html', {'movie': movie, 'rating':generate_star_counts(movie.vote_average)})

@login_required
def profile(request):

    def generate_star_counts(rating):
        # Split the rating into integer and decimal parts
        rating = round(rating * 2) / 2
        integer_part, decimal_part = divmod(rating, 1)

        # Determine the number of full, half, and empty stars
        full_stars = int(integer_part)
        half_star = 1 if decimal_part >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star

        # Return the list representing the star counts
        return [full_stars, half_star, empty_stars]
    
    user = request.user
    # Access user information
    username = user.username
    email = user.email

    flag = 1

    if request.method == 'POST':
        rating_id_to_delete = request.POST.get('rating_id_to_delete')

        if rating_id_to_delete:
            Rating.objects.filter(id=rating_id_to_delete).delete()
            user_matrix = create_csr_matrix_for_user(user.id)

            flag = 0

            als.partial_fit_users([162542+user.id], user_matrix)
            als.save('homepage/models_data/als_model.npz')
    
    # Query ratings for the given user
    user_ratings = Rating.objects.filter(user=user)

    # Create a list to store movie-rating pairs for the user
    user_movie_ratings = []
    personal_recommendations = []

    # Iterate through each rating and extract movie and rating information
    for rating in user_ratings:
        movie = rating.movie
        movie_id = movie.id
        movie_title = movie.title
        rating_value = generate_star_counts(rating.rating)
        user_movie_ratings.append((rating.id, movie_id, movie_title, rating_value))

    if len(user_ratings) > 0:

        if flag:
            user_matrix = create_csr_matrix_for_user(user.id)
        
        rec_ids, _ = als.recommend([162542+user.id], user_matrix, N=8)

        for id in rec_ids[0]:
            movie = Movie.objects.get(pk=id+1)
            movie_id = movie.id
            movie_title = movie.title
            personal_recommendations.append((movie_id, movie_title))

    return render(request, "homepage/profile.html", 
                  {'username': username, 
                   'email': email, 
                   'user_movie_ratings': user_movie_ratings,
                   'personal_recommendations': personal_recommendations })