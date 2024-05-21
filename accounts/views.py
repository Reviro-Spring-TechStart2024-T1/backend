from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from establishments.models import Establishment
from menu.permissions import IsAdminUser

from .models import User
from .serializers import (
    BlockPartnerSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
    PartnerUserRegisterSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.save()
            return Response(
                tokens,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary='Retrieve a list of all users.',
        description=(
            f'Retrieve a paginated list of all users that are registered in the system.\n'
            f'- Default elements per page 10.\n'
            f'- Permissions: Admin only.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            # Set new password
            self.object.set_password(serializer.validated_data['password'])
            self.object.save()
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    '''
    Refresh token has to be passed to log out user and put their refresh token into blacklist.
    '''

    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PartnerListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role__in=['partner'])
    serializer_class = PartnerUserRegisterSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary='Retrieve a list of all partners.',
        description=(
            f'Retrieve a paginated list of all partners that are registered in the system.\n'
            f'- Default elements per page 10.\n'
            f'- Permissions: Admin only.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create partner.',
        description=(
            f'Create partner by passing only email of designated user.\n'
            f'- Uniqueness of passed email will be checked, if email is in the db error will be raised\n'
            f'- Secure password is generated on the backend and letter is sent to new partner.\n'
            f'- Permissions: Admin only.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BlockPartnerView(generics.UpdateAPIView):
    queryset = User.objects.filter(role='partner')
    serializer_class = BlockPartnerSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    @extend_schema(
        summary='Block a partner.',
        description=(
            'Block a partner by setting the is_blocked field to True.\n'
            '- All related establishments will be marked as inactive.\n'
            '- Permissions: Admin only.'
        )
    )
    def update(self, request, *args, **kwargs):
        partner = self.get_object()
        partner.is_blocked = True
        partner.save()

        # Make all establishments of this partner as inactive
        Establishment.objects.filter(owner=partner).update(is_active=False)

        return Response(
            {'message': 'Partner has been blocked and establishments disabled'}, status=status.HTTP_200_OK
        )


class UnblockPartnerView(generics.UpdateAPIView):
    queryset = User.objects.filter(role='partner')
    serializer_class = BlockPartnerSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    @extend_schema(
        summary='Unblock a partner.',
        description=(
            'Unblock a partner by setting the is_blocked field to False.\n'
            '- All related establishments will be marked as active.\n'
            '- Permissions: Admin only.'
        )
    )
    def update(self, request, *args, **kwargs):
        partner = self.get_object()
        partner.is_blocked = False
        partner.save()

        # Make all establishments of this partner as active
        Establishment.objects.filter(owner=partner).update(is_active=True)

        return Response(
            {'message': 'Partner has been unblocked and establishments enabled'}, status=status.HTTP_200_OK
        )
