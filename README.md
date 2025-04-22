# License Insight Scraper API

**License Insight** is an API developed in Python that performs web scraping of data from the official INATRO website and summarizes essential information for developing a mobile application that queries the digital driver's license in Mozambique. This project is a simple personal learning experience focused on collecting and organizing relevant information.

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

- Clonar o repositório
```bash
git clone https://github.com/PedroNhamirre/License-Insight-Scraper-API.git
cd License-Insight-Scraper-API/inattro
```
- Criar um ambiente virtual e activar para Linux/macOS
```
python3 -m venv venv
source venv/bin/activate    
```
- Criar um ambiente virtual e activar para ara Windows
```
python3 -m venv venv
venv\Scripts\activate     
```
-  Instalar as dependências
```
pip3 install -r requirements.txt
```
- Aplicar as migrações do Django
```
python3 manage.py migrate
```
- Iniciar o servidor de desenvolvimento
```
python3 manage.py runserver
```

### API Documentation

To view the API documentation and test the endpoints, you can access the Swagger UI at `http://localhost:8000/swagger/`.

License Insight is made with ❤️ por ***Pedro Nhamirre***.

Feel free to reach out if you need any more assistance or adjustments!
