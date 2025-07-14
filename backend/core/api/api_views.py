from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.forms import CustomUserCreationForm
from core.forms import CustomAuthenticationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


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


class LoginAPIView(APIView):
    def post(self, request):
        form = CustomAuthenticationForm(request=request, data=request.data)

        if not form.is_valid():
            errors = {
                field: [str(error) for error in errs]
                for field, errs in form.errors.items()
            }
            return Response(
                {"errors": errors, "detail": "Por favor, corrija os erros abaixo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = form.get_user()
        login(request, user)
        return Response(
            {"detail": "Login realizado com sucesso!"}, status=status.HTTP_200_OK
        )


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})
