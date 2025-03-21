from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('set-model/', views.set_model_settings, name='set_model'),
    path('reset/', views.reset_settings, name='reset_model'),
    path('delete-file/<str:filename>/', views.delete_file, name='delete_file'),
    path('upload-file-only/', views.upload_file_only, name='upload_file_only'),
    
    path('add-rule/', views.add_rule, name='add_rule'),
    path('delete-rule/<path:rule>/', views.delete_rule, name='delete_rule'),
    path("add-link/", views.add_link, name="add_link"),
    path("delete-link/<path:link>/", views.delete_link, name="delete_link"),

]
