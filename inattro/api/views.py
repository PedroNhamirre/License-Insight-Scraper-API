from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ConsultaSerializer
from bs4 import BeautifulSoup
import requests
import json

# URLs do endpoint
login_url = 'https://balcaovirtual.inatro.gov.mz/app/ajax/auth/login.php'
license_status_url = 'https://balcaovirtual.inatro.gov.mz/estado_carta.php'
driving_ticket_url = 'https://balcaovirtual.inatro.gov.mz/consulta_multas.php'

class ConsultaAPIView(APIView):
    @swagger_auto_schema(
        request_body=ConsultaSerializer,
        responses={
            200: openapi.Response(
                description="Informações da carta e multas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'info_carta': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'numero_carta': openapi.Schema(type=openapi.TYPE_STRING),
                                'nome_completo': openapi.Schema(type=openapi.TYPE_STRING),
                                'data_nascimento': openapi.Schema(type=openapi.TYPE_STRING),
                                'telefone': openapi.Schema(type=openapi.TYPE_STRING),
                                'endereco': openapi.Schema(type=openapi.TYPE_STRING),
                                'estado_carta': openapi.Schema(type=openapi.TYPE_STRING),
                                'data_inicio_validade': openapi.Schema(type=openapi.TYPE_STRING),
                                'data_fim_validade': openapi.Schema(type=openapi.TYPE_STRING),
                                'classes_carta': openapi.Schema(type=openapi.TYPE_STRING),
                                'categorias_carta': openapi.Schema(type=openapi.TYPE_STRING),
                                'doc_number': openapi.Schema(type=openapi.TYPE_STRING),
                                'pais_de_origem': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'multas': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, additional_properties=openapi.Schema(type=openapi.TYPE_STRING))
                        ),
                    }
                )
            ),
            400: "Erro de entrada",
            500: "Erro interno do servidor"
        }
    )
    def post(self, request):
        serializer = ConsultaSerializer(data=request.data)
        if serializer.is_valid():
            codigo = serializer.validated_data['codigo']
            data_nascimento = serializer.validated_data['data_nascimento']

            session = requests.Session()

            # Login data
            payload = {
                "n_carta": codigo,
                "data_nascimento": data_nascimento,
            }

            # Realizar o login
            try:
                response = session.post(login_url, data=payload)
                response.raise_for_status()
                data = response.json()

                if not data.get("error"):
                    # Obter o estado da carta
                    response = session.get(license_status_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    card = soup.find('div', class_='card-body')
                    info_carta = {}

                    if card:
                        # Extrair informações da carta
                        info_carta["numero_carta"] = card.find('h5', string='Nº da Carta de Condução:').find_next('p').text.strip()
                        info_carta["nome_completo"] = card.find('h5', string='Nome completo:').find_next('p').text.strip()
                        info_carta["data_nascimento"] = card.find('h5', string='Data de nascimento:').find_next('p').text.strip()
                        info_carta["telefone"] = card.find('h5', string='Telefone:').find_next('p').text.strip()
                        info_carta["endereco"] = card.find('h5', string='Endereço:').find_next('p').text.strip()
                        info_carta["estado_carta"] = card.find('h5', string='Estado da carta:').find_next('p').text.strip()
                        info_carta["data_inicio_validade"] = card.find('h5', string='Data de ínicio de validade:').find_next('p').text.strip()
                        info_carta["data_fim_validade"] = card.find('h5', string='Data de fim de validade:').find_next('p').text.strip()
                        info_carta["classes_carta"] = card.find('h5', string='Classes da Carta:').find_next('p').text.strip()
                        info_carta["categorias_carta"] = card.find('h5', string='Categorias da Carta:').find_next('p').text.strip()

                        # Consultar multas
                        response = session.get(driving_ticket_url)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Extrair o doc_number do input hidden
                        doc_number_input = soup.find('input', {'id': 'dados_utente'})
                        if doc_number_input:
                            try:
                                dados_utente = json.loads(doc_number_input['value'])
                                info_carta["doc_number"] = dados_utente.get('doc_number')
                                info_carta["pais_de_origem"] = dados_utente.get('extra', {}).get('paisDeOrigemDescricao', 'Desconhecido')
                            except (ValueError, KeyError):
                                return Response({"error": "Erro ao processar os dados do usuário."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        # Extração de multas
                        multas = []
                        multas_table = soup.find('table')  # Ajuste o seletor conforme necessário
                        if multas_table:
                            for row in multas_table.find_all('tr')[1:]:  # Ignorar o cabeçalho
                                columns = row.find_all('td')
                                multa_info = [col.text.strip() for col in columns]
                                multas.append(multa_info)

                        # Retornar os dados
                        return Response({
                            "info_carta": info_carta,
                            "multas": multas
                        }, status=status.HTTP_200_OK)

                else:
                    return Response({"error": data.get("message")}, status=status.HTTP_400_BAD_REQUEST)

            except requests.HTTPError as http_err:
                return Response({"error": f"Erro de conexão: {http_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except ValueError:
                return Response({"error": "Erro ao processar a resposta do servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_date(self, date_str):
        """Valida se a data está no formato YYYY-MM-DD."""
        try:
            year, month, day = map(int, date_str.split('-'))
            return (1 <= month <= 12) and (1 <= day <= 31) and (1900 <= year <= 2100)  # Validações simples
        except ValueError:
            return False
