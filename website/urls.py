from django.urls import path
from .views import RegisterView, LoginView, LogoutView, question_list, question_detail, question_create, \
question_update, question_delete, answer_create, answer_edit, answer_delete, comment_create, comment_update, \
comment_delete

urlpatterns = [
################# REGISTRATION #################
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

################# QUESTIONS #################
    path('questions/', question_list, name='question_list'),
    path('questions/<int:pk>/', question_detail, name='question_detail'),
    path('questions/create/', question_create, name='question_create'),
    path('questions/update/<int:pk>/', question_update, name='question_update'),
    path('questions/delete/<int:pk>/', question_delete, name='question_delete'),

################# ANSWER #################
    path('questions/<int:pk>/answers/', answer_create, name='answer_create'),
    path('answer/update/<int:pk>/', answer_edit, name='answer_update'),
    path('answer/delete/<int:pk>/', answer_delete, name='answer_delete'),

################# COMMENT #################
    path('questions/<int:pk>/comments/', comment_create, name='comment_create'),
    path('comments/update/<int:pk>/', comment_update, name='comment_update'),
    path('comments/delete/<int:pk>/', comment_delete, name='comment_delete'),
]
