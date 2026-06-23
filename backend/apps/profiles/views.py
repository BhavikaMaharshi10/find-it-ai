from rest_framework import generics

from .models import Profile
from .serializers import ProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
