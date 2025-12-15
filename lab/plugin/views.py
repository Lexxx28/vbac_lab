from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Plugin
from .serializers import PluginSerializer
from user.permissions import AnyOfGroups
from django.db import models

class PluginViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Plugins to be viewed or edited.
    """
    queryset = Plugin.objects.all().order_by("-created_at")
    serializer_class = PluginSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'retrieve': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'list': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])
    
    
    # === CREATE Plugin, status is draft by default ===
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(is_active=False)
    
    # === UPDATE Plugin ===
    def perform_update(self, serializer):
        serializer.save(); return
    
    
    # === DELETE Plugin ===
    def perform_destroy(self, instance):
        instance.delete(); return