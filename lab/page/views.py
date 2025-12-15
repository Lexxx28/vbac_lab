from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Page
from .serializers import PageSerializer
from user.permissions import AnyOfGroups
from django.db import models

class PageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Pages to be viewed or edited.
    """
    queryset = Page.objects.all().order_by("-created_at")
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor')],
            'retrieve': [permissions.AllowAny()],
            'list': [permissions.AllowAny()],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])
    
    
    # === CREATE Page, status is draft by default ===
    def perform_create(self, serializer):
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        if not in_groups('Super Admin', 'Administrator', 'Editor'):
            raise PermissionDenied("You are not allowed to create Pages.")
        
        serializer.save(author=user, status='draft')
    
    # === UPDATE Page ===
    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        new_data = serializer.validated_data
        
        new_status = new_data.get('status', instance.status)
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        # === Page OWNER ===
        if instance.author == user:
            if new_status == 'publish' and in_groups('Super Admin', 'Administrator', 'Editor'):
                serializer.save(author=instance.author); return
            elif new_status == 'publish':
                raise PermissionDenied("Only Super Admin, Administrator, Editor, Author can publish Pages, Even if you are the owner.")
            
            if new_status == 'private' and in_groups('Super Admin', 'Administrator', 'Editor'):
                serializer.save(author=instance.author); return
            elif new_status == 'private':
                raise PermissionDenied("Only Super Admin, Administrator, Editor can set posts to private, Even if you are the owner.")
            
            if new_status == 'draft':
                serializer.save(author=instance.author); return
        
        # === NON POST OWNER ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            serializer.save(author=instance.author); return
        else:
            raise PermissionDenied("You are not allowed to update this post.")
        
    
    
    # === DELETE POST ===
    def perform_destroy(self, instance):
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        # === POST OWNER ===
        if instance.author == user:
            if instance.status == 'publish' and in_groups('Super Admin', 'Administrator', 'Editor', 'Author'):
                instance.delete(); return
            elif instance.status == 'publish':
                raise PermissionDenied("Only Super Admin, Administrator, Editor, Author can delete published posts, Even if you are the owner.")
            
            if instance.status == 'private' and in_groups('Super Admin', 'Administrator', 'Editor'):
                instance.delete(); return
            elif instance.status == 'private':
                raise PermissionDenied("Only Super Admin, Administrator, Editor can delete private posts, Even if you are the owner.")
            
            if instance.status == 'draft':
                instance.delete(); return
        
        # === NON POST OWNER ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            instance.delete(); return
        else:
            raise PermissionDenied("You are not allowed to delete this post.")
        
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)

        # === ADMIN/EDITOR/AUTHOR/CONTRIBUTOR CAN SEE ALL POSTS ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            return qs
        
        # === AUTHENTICATED USER CAN SEE THEIR OWN POSTS AND PUBLIC POSTS ===
        if user.is_authenticated:
            return qs.filter(models.Q(status='publish') | models.Q(author=user))
        else:
            # === ANONYMOUS USER CAN ONLY SEE PUBLISHED POSTS ===
            return qs.filter(status='publish')
        

