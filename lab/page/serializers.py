from rest_framework import serializers
from .models import Page


class PageSerializer(serializers.HyperlinkedModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Page
        fields = ['id', 'title', 'content', 'author', 'author_username', 'status', 'created_at']
        read_only_fields = ['created_at', 'updated_at']
