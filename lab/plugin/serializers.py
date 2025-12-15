from rest_framework import serializers
from .models import Plugin


class PluginSerializer(serializers.HyperlinkedModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Plugin
        fields = ['id', 'name', 'version', 'is_active', 'settings']
        read_only_fields = ['created_at', 'updated_at']

    def __str__(self):
        return f"{self.name} ({self.version})"