from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post


class PostSerializer(serializers.HyperlinkedModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_username', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

