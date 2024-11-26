from django.urls import path
from .views import RegisterView, LoginView, LogoutView, question_list, question_detail, question_create, \
question_update, question_delete

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('questions/', question_list, name='question_list'),
    path('questions/<int:pk>/', question_detail, name='question_detail'),
    path('questions/create/', question_create, name='question_create'),
    path('questions/update/<int:pk>/', question_update, name='question_update'),
    path('questions/delete/<int:pk>/', question_delete, name='question_delete'),
]
