import requests
import json

# Testar a API
API_URL = "https://www.chavesnamao.com.br/api/realestate/listing/items/?"

# Fazer requisição
response = requests.get(API_URL)

print(f"Status Code: {response.status_code}")
print(f"URL: {response.url}")

if response.status_code == 200:
    data = response.json()
    
    # Salvar resposta completa para análise
    with open("api_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nTipo de resposta: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Chaves principais: {list(data.keys())}")
        
        # Se tiver uma lista de itens, mostrar o primeiro
        for key in ['items', 'results', 'data', 'listings', 'imoveis']:
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                print(f"\nPrimeiro item de '{key}':")
                print(json.dumps(data[key][0], indent=2, ensure_ascii=False)[:1000])
                break
    
    elif isinstance(data, list) and len(data) > 0:
        print(f"Total de itens: {len(data)}")
        print("\nPrimeiro item:")
        print(json.dumps(data[0], indent=2, ensure_ascii=False)[:1000])
else:
    print(f"Erro: {response.text}")