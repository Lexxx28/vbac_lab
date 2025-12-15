from django.contrib.auth.models import Group, User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "password", "email", "groups"]
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        """
        Create and return a new user instance with hashed password.
        """
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', [])  # Extract groups (many-to-many)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)  # Hash the password
            user.save()
        if groups:
            user.groups.set(groups)  # Set groups using .set() method
        return user
    
    def update(self, instance, validated_data):
        """
        Update and return an existing user instance with hashed password if provided.
        """
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)  # Extract groups (many-to-many)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)  # Hash the password
        
        instance.save()
        
        if groups is not None:  # Only update if groups were provided
            instance.groups.set(groups)  # Set groups using .set() method
        
        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]