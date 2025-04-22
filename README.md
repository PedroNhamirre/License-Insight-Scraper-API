# License Insight Scraper API

**License Insight** is an API developed purely for personal learning purposes using Python and Django. The project performs web scraping from the official INATRO website and summarizes relevant data for a potential mobile application that queries digital driver's license information in Mozambique.


>[!WARNING]  
>This project is **not production-ready**. It was built as a hands-on learning experience focused on data collection and organization.

## Description
License Insight is designed to collect relevant data from the INATRO website and present this information in an organized and accessible manner. The API serves as an intermediary to facilitate the query of information regarding the digital driver's license in Mozambique, improving accessibility and user experience.

## Features

- Web scraping of data from the official website
- Summary and organization of collected information
- Preparation of data for integration into a mobile application

## 🚀 Technologies Used

- Python 3
- Django
- BeautifulSoup
- Requests

## Dependencies

The necessary dependencies are listed in the `requirements.txt` file.

## ⚙️ Requirements

To install and run License Insight, you will need the following tools:

- **Python 3**
- **Git**
- **Pip3**

### Installation

Execute the following commands to install the dependencies:

- Clone the repository
```bash
git clone https://github.com/PedroNhamirre/License-Insight-Scraper-API.git
cd License-Insight-Scraper-API/inattro
```
- Create and activate a virtual environment for Linux/macOS
```
python3 -m venv venv
source venv/bin/activate    
```
- Create and activate a virtual environment for Windows
```
python3 -m venv venv
venv\Scripts\activate     
```
- Install the dependencies
```
pip3 install -r requirements.txt
```
- Apply Django migrations
```
python3 manage.py migrate
```
- Start the development server
```
python3 manage.py runserver
```

### Main Endpoint

You can test the driver's license query locally at:
```
POST http://localhost:8000/api/consulta/
```
#### Request Body (JSON)

```json
{
  "codigo": "string",
  "data_nascimento": "YYYY-MM-DD"
}
```
`codigo:` The license code/number.

`data_nascimento:` The date of birth associated with the license (format: YYYY-MM-DD).


#### Response Example (JSON)
```json
{
  "info_carta": {
    "numero_carta": "123456789",
    "nome_completo": "Pedro Nhamirre",
    "data_nascimento": "1995-06-15",
    "telefone": "+258840000000",
    "endereco": "Av. da Liberdade, Beira",
    "estado_carta": "Válida",
    "data_inicio_validade": "2020-01-01",
    "data_fim_validade": "2030-01-01",
    "classes_carta": "A, B",
    "categorias_carta": "Ligeiros, Motociclos",
    "doc_number": "A12345678",
    "pais_de_origem": "Moçambique"
  },
  "multas": []
}
```


This endpoint is also available and testable via Swagger at: ```http://localhost:8000/swagger/```

License Insight is made with ❤️ por ***Pedro Nhamirre***.
