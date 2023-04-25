from django.urls import path

from . import views

urlpatterns = [
    path('text_search', views.text_search, name='text_search'),
    path('video_search', views.video_search, name='video_search'),
    path('add_index', views.add_index, name='add_index'),
    path('explain_query', views.explain_query, name='explain_query'),
    path('about', views.about, name='about'),
]
