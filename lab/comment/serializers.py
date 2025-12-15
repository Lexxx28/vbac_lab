from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source='author.username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'author_username',
            'content',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
