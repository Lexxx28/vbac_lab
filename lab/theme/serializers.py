from rest_framework import serializers
from .models import Theme


class ThemeSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Theme
        fields = ['id', 'name', 'version', 'is_active', 'options']
        read_only_fields = ['created_at', 'updated_at']

    def __str__(self):
        return f"{self.name} ({self.version})"