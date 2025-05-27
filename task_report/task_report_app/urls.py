from django.urls import path
from . import views

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('add/', views.add_card, name='add_card'),
    path('edit/<int:card_id>/', views.edit_card, name='edit_card'),
    path('delete/<int:card_id>/', views.delete_card, name='delete_card'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("register/", views.register_user, name="register"),
    path('archive/', views.archive_list, name='archive')
]