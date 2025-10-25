from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

# =======================
#  REGISTER USER
# =======================
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # validate manually so we return clean field errors JSON (email/username)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # still return tokens if you want — frontend will not auto-save on register
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


# =======================
#  LOGIN USER
# =======================
class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # if invalid, return a clean JSON error the frontend can parse
        if not serializer.is_valid():
            errors = serializer.errors or {}
            # Prefer non_field_errors, otherwise take first field error message
            if 'non_field_errors' in errors:
                message = errors['non_field_errors'][0]
            else:
                # pick first available message
                message = None
                for k, v in errors.items():
                    if isinstance(v, list) and len(v) > 0:
                        message = v[0]
                        break
                    elif isinstance(v, str):
                        message = v
                        break
                if not message:
                    message = 'Invalid email/username or password.'
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        # valid: return tokens + user
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
