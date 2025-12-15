from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Theme
from .serializers import ThemeSerializer
from user.permissions import AnyOfGroups
from django.db import models

class ThemeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Themes to be viewed or edited.
    """
    queryset = Theme.objects.all().order_by("-created_at")
    serializer_class = ThemeSerializer
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
    
    
    # === CREATE Theme, status is draft by default ===
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(is_active=False)
    
    # === UPDATE Theme ===
    def perform_update(self, serializer):
        serializer.save(); return
    
    
    # === DELETE Theme ===
    def perform_destroy(self, instance):
        instance.delete(); return