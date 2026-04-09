from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from users.permissions import IsAdmin, IsAnalyst, IsViewer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        return [IsAdmin()]