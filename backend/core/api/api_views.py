from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.forms import CustomUserCreationForm


class RegisterAPIView(APIView):
    def post(self, request):
        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user = form.save()
            return Response(
                {
                    "message": (
                        f"Usuário {user.username} registrado com sucesso! "
                        f"Faça login agora."
                    ),
                    "username": user.username,
                    "public_id": str(user.public_id),
                },
                status=status.HTTP_201_CREATED,
            )
        errors = {}
        for field, field_errors in form.errors.items():
            errors[field] = [str(e) for e in field_errors]
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
