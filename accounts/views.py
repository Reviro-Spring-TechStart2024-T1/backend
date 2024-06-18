from django_rest_passwordreset.views import (
    ResetPasswordConfirmViewSet,
    ResetPasswordRequestTokenViewSet,
    ResetPasswordValidateTokenViewSet,
)
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from menu.permissions import IsAdminUser

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    CustomObtainTokenPairSerializer,
    LogoutSerializer,
    PartnerBlockUnblockSerializer,
    PartnerUserRegisterSerializer,
    UserProfileSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Create user',
        description=(
            'By default if anyone creating through this endpoint an account for themselves '
            'will be creating a user instance with `customer` role.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
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

    @extend_schema(
        summary='Get profile',
        description=(
            'Show\'s details of a user without passing user id to the endpoint.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Update profile',
        description=(
            'Allows user to update their profile.\n'
            '- Requires authentication.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update profile',
        description=(
            'Allows user to partially update their profile.\n'
            '- Requires authentication.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


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

    @extend_schema(
        summary='Update password',
        description=(
            'Allows authenticated user to update password.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update password',
        description=(
            'Allows authenticated user to partially update password.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class LogoutView(generics.GenericAPIView):
    '''
    Refresh token has to be passed to log out user and put their refresh token into blacklist.
    '''

    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Logout user',
        description=(
            'Refresh token has to be passed to log out user and put their refresh token into blacklist.\n'
            '- Requires authentication.\n'
            '- Permissions: Allowed to anyone.'
        )
    )
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


class BlockPartnerView(views.APIView):
    serializer_class = PartnerBlockUnblockSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary='Block partner',
        description=(
            'Allows admin to block partner, under the hood soft delete\'s manager '
            'options are utilized to achieve blocking of a partner.\n'
            '- Requires authentication.\n'
            '- Permissions: Admin only.'
        )
    )
    def patch(self, request, format=None):
        return self.update_block_status(request, True)

    def update_block_status(self, request, is_blocked=True):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner = User.objects.get(email=email)
            if partner.role == 'partner':
                partner.is_blocked = is_blocked
                partner.save()
                serializer = PartnerBlockUnblockSerializer(partner)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Given user is not of role partner.'})
        except User.DoesNotExist:
            return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)


class UnblockPartnerView(views.APIView):
    serializer_class = PartnerBlockUnblockSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary='Unblock partner',
        description=(
            'Allows admin to unblock partner, under the hood soft delete\'s manager '
            'options are utilized to achieve unblocking of a partner.\n'
            '- Requires authentication.\n'
            '- Permissions: Admin only.'
        )
    )
    def patch(self, request, format=None):
        return self.update_block_status(request, False)

    def update_block_status(self, request, is_unblocked=False):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner = User.objects.get(email=email)
            if partner.role == 'partner':
                partner.is_blocked = is_unblocked
                partner.save()
                serializer = PartnerBlockUnblockSerializer(partner)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Given user is not of role partner.'})
        except User.DoesNotExist:
            return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Validate token",
    description=(
        "This endpoint allows you to validate a reset password token. "
        "It ensures the token is valid and has not expired.\n"
        "- Permissions: Allowed to anyone."
    )
)
class CustomResetPasswordValidateTokenViewSet(ResetPasswordValidateTokenViewSet):
    pass


@extend_schema(
    summary="Confirm reset",
    description=(
        "This endpoint allows you to confirm a password reset. "
        "It takes the token and the new password and updates the user's password.\n"
        "- Permissions: Allowed to anyone."
    )
)
class CustomResetPasswordConfirmViewSet(ResetPasswordConfirmViewSet):
    pass


@extend_schema(
    summary="Request token",
    description=(
        "This endpoint allows you to request a password reset token. "
        "You need to provide the email associated with the user account.\n"
        "- Permissions: Allowed to anyone."
    )
)
class CustomResetPasswordRequestTokenViewSet(ResetPasswordRequestTokenViewSet):
    pass


@extend_schema(
    summary="Obtain JWT token",
    description="This endpoint allows you to obtain a new JWT token pair "
    "(access and refresh token) and users role by providing valid user credentials.\n"
    "- Permissions: Allowed to anyone."
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomObtainTokenPairSerializer


@extend_schema(
    summary="Refresh JWT token",
    description="This endpoint allows you to refresh your JWT access token using a valid refresh token."
)
class CustomTokenRefreshView(TokenRefreshView):
    pass
