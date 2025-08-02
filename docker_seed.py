#!/usr/bin/env python3
"""
Script para carregar dados no sistema usando containers Docker
"""
import os
import json
from pathlib import Path
import requests
import time

def wait_for_api():
    """Aguarda a API ficar disponível"""
    print("🔍 Aguardando API ficar disponível...")
    max_retries = 60  # Aumentado para 60 tentativas (2 minutos)
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8001/", timeout=5)
            if response.status_code == 200:
                print("API disponível!")
                print("Aguardando API estabilizar...")
                time.sleep(5)
                return True
        except requests.exceptions.RequestException as e:
            if i == 0:
                print(f"Detalhes: {e}")
        
        print(f"⏳ Tentativa {i+1}/{max_retries}...")
        time.sleep(2)
    
    print("API não ficou disponível")
    print("Dica: Verifique se os containers estão rodando com 'docker ps'")
    print("Veja os logs com 'docker logs spd_api'")
    return False

def load_imoveis_from_files():
    """Carrega imóveis dos arquivos JSON"""
    possible_paths = [
        Path("../anuncios_salvos"),
        Path("./anuncios_salvos"),
        Path.home() / "SPD" / "anuncios_salvos",
        Path(os.environ.get("ANUNCIOS_SALVOS_PATH", "")),
    ]
    
    imoveis_dir = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            imoveis_dir = path
            break
    
    if not imoveis_dir:
        raise FileNotFoundError("Diretório 'anuncios_salvos' não encontrado")
    
    imoveis = []
    for folder_name in sorted(os.listdir(imoveis_dir), key=int):
        folder = imoveis_dir / folder_name
        if folder.is_dir():
            info_file = folder / "info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    imovel = {
                        "titulo": data.get('title', ''),
                        "descricao": data.get('full_description', ''),
                        "especificacoes": [
                            data.get('property_type_area', ''),
                            data.get('bedrooms', ''),
                            data.get('address_line1', ''),
                            data.get('address_line2', ''),
                            f"Preço: {data.get('price', '')}"
                        ] + data.get('characteristics', [])
                    }
                    imoveis.append(imovel)
                    
                except Exception as e:
                    print(f"Erro ao processar {info_file}: {e}")
    
    return imoveis

def clear_existing_data():
    """Limpa dados existentes no MongoDB e ChromaDB"""
    print("Limpando dados existentes...")
    
    try:
        # Limpar MongoDB
        response = requests.delete("http://localhost:8001/imoveis/all", timeout=30)
        if response.status_code in [200, 204]:
            print("MongoDB limpo")
        else:
            print(f"Aviso: Não foi possível limpar MongoDB (status: {response.status_code})")
        
        # Limpar ChromaDB 
        response = requests.delete("http://localhost:8001/search/clear", timeout=30)
        if response.status_code in [200, 204]:
            print("ChromaDB limpo")
        else:
            print(f"Aviso: Não foi possível limpar ChromaDB (status: {response.status_code})")
            
        print("Limpeza concluída")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Aviso: Erro na limpeza: {e} (continuando...)")
        return True  # Continua mesmo se a limpeza falhar

def load_data_via_api():
    """Carrega dados usando API diretamente"""
    print("Carregando imóveis via API...")
    
    # Limpar dados existentes primeiro
    if not clear_existing_data():
        return False
    
    try:
        imoveis = load_imoveis_from_files()
        print(f"Encontrados {len(imoveis)} imóveis para carregar")
    except FileNotFoundError as e:
        print(f"{e}")
        return False
    
    # Carregar dados via API
    success_count = 0
    error_count = 0
    
    for i, imovel in enumerate(imoveis, 1):
        try:
            response = requests.post(
                "http://localhost:8001/imoveis/",
                json=imovel,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                success_count += 1
                if i % 20 == 0:  # Log a cada 20 imóveis
                    print(f"Processados: {i}/{len(imoveis)}")
            else:
                error_count += 1
                print(f"Erro no imóvel {i}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            error_count += 1
            print(f"Erro na requisição {i}: {e}")
    
    print(f"\nProcessamento concluído!")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    print(f"Total: {len(imoveis)}")
    
    return success_count > 0

def main():
    print("🏠 SPD Imóveis - Carregamento de Dados")
    print("=====================================")
    
    if not wait_for_api():
        return False
    
    return load_data_via_api()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)