from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from unidecode import unidecode  # Importa a função para remover acentos

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o Flask com o argumento necessário
app = Flask(__name__)  # Passa o nome do módulo ao Flask
CORS(app)  # Habilita CORS

# Função para remover acentos
def remove_acentos(texto):
    return unidecode(texto)

PORT = os.getenv("PORT", 5000)  # Porta padrão
API_KEY = os.getenv("API_KEY")  # Chave da API do clima

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server!", 200

# Rota para buscar informações do clima
@app.route('/weather/<string:city>/<string:uf>', methods=['GET'])
def get_weather(city, uf):
    try:
        # Chamada à API do IBGE para verificar se a cidade pertence à UF
        ibge_url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        ibge_response = requests.get(ibge_url)
        
        # Remover acentos do nome dos municípios
        municipios = [remove_acentos(municipio['nome'].lower()) for municipio in ibge_response.json()]
        
        # Verificar se a cidade pertence à lista de municípios
        cidade_formatada = remove_acentos(city.lower())
        if cidade_formatada not in municipios:
            return jsonify({"error": "A cidade não corresponde à UF fornecida."}), 400

        # Chamada para o clima atual
        current_weather_url = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={cidade_formatada},{uf}&lang=pt"
        current_weather_response = requests.get(current_weather_url)

        # Chamada para a previsão do tempo
        forecast_url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={cidade_formatada},{uf}&days=3&lang=pt"
        forecast_response = requests.get(forecast_url)

        if current_weather_response.status_code == 200 and forecast_response.status_code == 200:
            return jsonify({
                "current": current_weather_response.json(),
                "forecast": forecast_response.json()['forecast']['forecastday']
            })
        else:
            raise Exception("API call failed")

    except requests.exceptions.RequestException as e:
        print("Failed to fetch data:", e)
        return jsonify({"error": "Erro ao buscar dados da API de clima"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Erro desconhecido"}), 500

# Inicia o servidor
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(PORT))
