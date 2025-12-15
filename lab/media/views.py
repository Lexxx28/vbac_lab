from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Media
from .serializers import MediaSerializer
from user.permissions import  AnyOfGroups
from django.db import models

class MediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """
    queryset = Media.objects.all().order_by("-created_at")
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'retrieve': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor', 'Subscriber')],
            'list': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor', 'Subscriber')],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])
    
    
    # === CREATE POST, status is draft by default ===
    def perform_create(self, serializer):
        user = self.request.user
        
        serializer.save(author=user)
    
    # === UPDATE POST ===
    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        serializer.save(author=instance.author)
    
    
    # === DELETE POST ===
    def perform_destroy(self, instance):
        instance.delete()
        

