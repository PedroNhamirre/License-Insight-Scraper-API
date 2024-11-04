from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bs4 import BeautifulSoup
import requests
import json

# URLs do endpoint
login_url = 'https://balcaovirtual.inatro.gov.mz/app/ajax/auth/login.php'
license_status_url = 'https://balcaovirtual.inatro.gov.mz/estado_carta.php'
driving_ticket_url = 'https://balcaovirtual.inatro.gov.mz/consulta_multas.php'

class ConsultaAPIView(APIView):
    def post(self, request):
        codigo = request.data.get('codigo')
        data_nascimento = request.data.get('data_nascimento')

        # Validação básica dos da dosde entrada
        if not codigo or not data_nascimento:
            return Response({"error": "Código e data de nascimento são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        # Validação do formato da data
        if not self.validate_date(data_nascimento):
            return Response({"error": "Data de nascimento inválida. Use o formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)


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

    def validate_date(self, date_str):
        """Valida se a data está no formato YYYY-MM-DD."""
        try:
            year, month, day = map(int, date_str.split('-'))
            return (1 <= month <= 12) and (1 <= day <= 31) and (1900 <= year <= 2100)  # Validações simples
        except ValueError:
            return False
