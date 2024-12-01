from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Question, Answer, Comment, Profile, Favorite


################# REGISTRATION #################
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

################# PROFILE #################
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    favorite_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'birth_date', 'favorite_count']

    def get_favorite_count(self, obj):
        return Favorite.objects.filter(user=obj.user).count()


################# QUESTIONS #################
class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    class Meta:
        model = Question
        fields = '__all__'

################# ANSWER #################
class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'author', 'content', 'date_created']
        read_only_fields = ['question', 'author', 'date_created']

################# COMMENT #################
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'date_created']
        read_only_fields = ['id', 'author', 'date_created']

################# FAVORITE #################
class FavoriteSerializer(serializers.ModelSerializer):
    question = serializers.StringRelatedField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['id', 'author', 'question', 'added_at']
        read_only_fields = ['added_at']

    def get_author(self, obj):
        return obj.question.author.username