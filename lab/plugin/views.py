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
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        if not in_groups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor'):
            raise PermissionDenied("You are not allowed to create Plugins.")
        
        serializer.save(author=user, status='draft')
    
    # === UPDATE Plugin ===
    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        new_data = serializer.validated_data
        
        new_status = new_data.get('status', instance.status)
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        # === Plugin OWNER ===
        if instance.author == user:
            if new_status == 'publish' and in_groups('Super Admin', 'Administrator', 'Editor', 'Author'):
                serializer.save(author=instance.author); return
            elif new_status == 'publish':
                raise PermissionDenied("Only Super Admin, Administrator, Editor, Author can publish Plugins, Even if you are the owner.")
            
            if new_status == 'private' and in_groups('Super Admin', 'Administrator', 'Editor'):
                serializer.save(author=instance.author); return
            elif new_status == 'private':
                raise PermissionDenied("Only Super Admin, Administrator, Editor can set Plugins to private, Even if you are the owner.")
            
            if new_status == 'draft':
                serializer.save(author=instance.author); return
        
        # === NON Plugin OWNER ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            serializer.save(author=instance.author); return
        else:
            raise PermissionDenied("You are not allowed to update this Plugin.")
        
    
    
    # === DELETE Plugin ===
    def perform_destroy(self, instance):
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        # === Plugin OWNER ===
        if instance.author == user:
            if instance.status == 'publish' and in_groups('Super Admin', 'Administrator', 'Editor', 'Author'):
                instance.delete(); return
            elif instance.status == 'publish':
                raise PermissionDenied("Only Super Admin, Administrator, Editor, Author can delete published Plugins, Even if you are the owner.")
            
            if instance.status == 'private' and in_groups('Super Admin', 'Administrator', 'Editor'):
                instance.delete(); return
            elif instance.status == 'private':
                raise PermissionDenied("Only Super Admin, Administrator, Editor can delete private Plugins, Even if you are the owner.")
            
            if instance.status == 'draft':
                instance.delete(); return
        
        # === NON Plugin OWNER ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            instance.delete(); return
        else:
            raise PermissionDenied("You are not allowed to delete this Plugin.")
        
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)

        # === ADMIN/EDITOR/AUTHOR/CONTRIBUTOR CAN SEE ALL PluginS ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            return qs
        
        # === AUTHENTICATED USER CAN SEE THEIR OWN PluginS AND PUBLIC PluginS ===
        if user.is_authenticated:
            return qs.filter(models.Q(status='publish') | models.Q(author=user))
        else:
            # === ANONYMOUS USER CAN ONLY SEE PUBLISHED PluginS ===
            return qs.filter(status='publish')
        

