from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Comment
from .serializers import CommentSerializer
from user.permissions import AnyOfGroups
from django.db import models

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Comments to be viewed or edited.
    """
    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor', 'Subscriber')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor', 'Subscriber')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor', 'Subscriber')],
            'retrieve': [permissions.AllowAny()],
            'list': [permissions.AllowAny()],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])
    
    
    # === CREATE Comment, status is draft by default ===
    def perform_create(self, serializer):
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        serializer.save(author=user)
    
    # === UPDATE Comment ===
    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        new_data = serializer.validated_data
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        
        # === Comment OWNER ===
        if instance.author == user:
            serializer.save(author=instance.author)
        else:
            raise PermissionDenied("You are not allowed to update this Comment.")
        
    
    
    # === DELETE Comment ===
    def perform_destroy(self, instance):
        user = self.request.user
        
        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)
        # === Comment OWNER ===
        if instance.author == user:
            instance.delete(); return
        
        # === NON Comment OWNER ===
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            instance.delete(); return
        else:
            raise PermissionDenied("You are not allowed to delete this Comment.")
        
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        post_id = self.kwargs.get("post_id") # GET /api/posts/<int:post_id>/comments/

        def in_groups(*roles):
            return AnyOfGroups(*roles).has_permission(self.request, self)

        # filter by post id if provided
        if not post_id:
            raise ValidationError({
                "post_id": "This query parameter is required."
            })
            
        # admin/editor see all
        if in_groups('Super Admin', 'Administrator', 'Editor'):
            return qs

        # authenticated user
        if user.is_authenticated:
            return qs.filter(
                models.Q(post__status='publish') |
                models.Q(author=user)
            )

        # anonymous
        return qs.filter(post__status='publish')

        

