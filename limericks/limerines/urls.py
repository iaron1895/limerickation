from django.urls import path

from . import views

app_name = 'limerines'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('limericks/', views.all_limericks, name='limericks'),
    path('generate/', views.generate_limerick, name='generate'),
    path('limericks/<int:limerick_id>', views.detail, name='detail'),
    path('limericks/<int:limerick_id>/edit', views.detail, name='edit'),
    path('limericks/<int:limerick_id>/edit/result', views.detail, name='result'),
]