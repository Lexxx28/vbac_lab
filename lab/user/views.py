from django.contrib.auth.models import User, Group
from rest_framework import permissions, viewsets
from .serializers import UserSerializer, GroupSerializer
from .permissions import AnyOfGroups

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'retrieve': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor')],
            'list': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator', 'Editor', 'Author', 'Contributor')],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])
    

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        actions = {
            'create': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'update': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'destroy': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'retrieve': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
            'list': [permissions.IsAuthenticated(), AnyOfGroups('Super Admin', 'Administrator')],
        }
        return actions.get(self.action, [permissions.AND(permissions.IsAuthenticated(), permissions.NOT(permissions.IsAuthenticated()))])