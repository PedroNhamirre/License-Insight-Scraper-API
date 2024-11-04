from django.urls import path
from .views import ConsultaAPIView



urlpatterns = [
    path('consulta/', ConsultaAPIView.as_view(), name='consulta'),
]
