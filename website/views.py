from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from stackFlow import settings
from .serializers import RegisterSerializer, AnswerSerializer, CommentSerializer, ProfileSerializer, FavoriteSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404, render
from .models import Question, Answer, Comment, Profile, Favorite
from .serializers import QuestionSerializer
from django.db.models.signals import post_save
from django.dispatch import receiver

################# REGISTRATION #################
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

################# PROFILE #################
@api_view(['GET'])
def profile_view(request, pk):
    profile = get_object_or_404(Profile, user__id=pk)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_update(request, pk):

    if request.user.id != pk:
        return Response({"error": "You do not have permission to update this profile."}, status=status.HTTP_403_FORBIDDEN)

    profile = get_object_or_404(Profile, user__id=pk)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

################# QUESTIONS #################
@api_view(['GET'])
def question_list(request):
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def question_detail(request, pk):

    question = get_object_or_404(Question, pk=pk)
    answers = Answer.objects.filter(question=question)
    comments = Comment.objects.filter(question=question)

    question_serializer = QuestionSerializer(question)
    answer_serializer = AnswerSerializer(answers, many=True)
    comment_serializer = CommentSerializer(comments, many=True)

    return Response({
        "question": question_serializer.data,
        "answers": answer_serializer.data,
        "comments": comment_serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def question_create(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if question.author != request.user:
        return Response({"error": "You are not the author of this question"}, status=status.HTTP_403_FORBIDDEN)

    serializer = QuestionSerializer(question, data=request.data, partial=('PATCH' in request.method))
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if question.author != request.user:
        return Response({"error": "You are not the author of this question"}, status=status.HTTP_403_FORBIDDEN)

    question.delete()
    return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

################# ANSWER #################
@api_view(['GET'])
def answer_detail(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    serializer = AnswerSerializer(answer)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_create(request, pk):
    question = get_object_or_404(Question, pk=pk)
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():
        answer = serializer.save(author=request.user, question=question)

        mail_sent = send_mail(
            subject='New Answer Added',
            message=f"A new answer has been added to the question: {question.title}\n\nAnswer content: {answer.content}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['pierrenogaro@zohomail.eu'],
            fail_silently=True,
        )

        if mail_sent:
            return Response(
                {"message": "Answer created successfully, and email sent.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "Answer created successfully, but email could not be sent.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def answer_edit(request, pk):
    answer = get_object_or_404(Answer, pk=pk)

    if answer.author != request.user:
        return Response({"detail": "You do not have permission to edit this answer."}, status=status.HTTP_403_FORBIDDEN)

    serializer = AnswerSerializer(answer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def answer_delete(request, pk):
    answer = get_object_or_404(Answer, pk=pk)

    if answer.author != request.user:
        return Response({"detail": "You do not have permission to delete this answer."},status=status.HTTP_403_FORBIDDEN)

    answer.delete()
    return Response({"detail": "Answer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

################# COMMENT #################
@api_view(['GET'])
def comment_detail(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, pk):
    question = get_object_or_404(Question, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return Response({"error": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CommentSerializer(comment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return Response({"error": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

################# FAVORITE #################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, pk):
    question = get_object_or_404(Question, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, question=question)
    if created:
        return Response({"message": "Question added to favorites"}, status=status.HTTP_201_CREATED)
    return Response({"message": "Question is already in favorites"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, pk):
    favorite = get_object_or_404(Favorite, user=request.user, question_id=pk)
    favorite.delete()
    return Response({"message": "Question removed from favorites"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

################# DOC #################
def home(request):
    return render(request, 'index.html')