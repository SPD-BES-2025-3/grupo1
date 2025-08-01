import json
import os
from pathlib import Path
from src.app.database import get_mongo_repo, get_chroma_repo
from src.app.services.embedding_service import EmbeddingService
from src.app.services.indexing_service import IndexingService
from src.app.models import Imovel, ImovelInDB, PyObjectId
from bson import ObjectId

def load_imoveis_from_files():
    # Buscar diretório anuncios_salvos em locais possíveis
    possible_paths = [
        Path("../anuncios_salvos"),  # Relativo ao projeto
        Path("./anuncios_salvos"),   # No mesmo diretório
        Path.home() / "SPD" / "anuncios_salvos",  # Home do usuário
        Path(os.environ.get("ANUNCIOS_SALVOS_PATH", "")),  # Variável de ambiente
    ]
    
    imoveis_dir = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            imoveis_dir = path
            break
    
    if not imoveis_dir:
        raise FileNotFoundError(
            "Diretório 'anuncios_salvos' não encontrado. "
            "Verifique se existe em: ../anuncios_salvos, ./anuncios_salvos, "
            "~/SPD/anuncios_salvos ou defina ANUNCIOS_SALVOS_PATH"
        )
    imoveis = []
    
    for folder in imoveis_dir.iterdir():
        if folder.is_dir():
            info_file = folder / "info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    imovel = Imovel(
                        titulo=data.get('title', ''),
                        descricao=data.get('full_description', ''),
                        especificacoes=[
                            data.get('property_type_area', ''),
                            data.get('bedrooms', ''),
                            data.get('address_line1', ''),
                            data.get('address_line2', ''),
                            f"Preço: {data.get('price', '')}"
                        ] + data.get('characteristics', [])
                    )
                    imoveis.append(imovel)
                    
                except Exception as e:
                    print(f"Erro ao processar {info_file}: {e}")
    
    return imoveis

def main():
    print("Carregando imóveis dos arquivos...")
    try:
        imoveis = load_imoveis_from_files()
        print(f"Encontrados {len(imoveis)} imóveis")
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        print("💡 Dica: Coloque o diretório 'anuncios_salvos' em uma das localizações sugeridas")
        return
    
    mongo_repo = get_mongo_repo()
    chroma_repo = get_chroma_repo()
    embedding_service = EmbeddingService()
    indexing_service = IndexingService(embedding_service, chroma_repo)
    
    print("Salvando no MongoDB...")
    imoveis_salvos = []
    for imovel in imoveis:
        imovel_dict = imovel.model_dump()
        imovel_id = mongo_repo.add_imovel(imovel_dict)
        
        # Criar ImovelInDB usando o MESMO ID do MongoDB
        imovel_salvo = ImovelInDB(
            id=imovel_id,  # Usar diretamente o ID string retornado pelo MongoDB
            titulo=imovel.titulo,
            descricao=imovel.descricao,
            especificacoes=imovel.especificacoes
        )
        imoveis_salvos.append(imovel_salvo)
    
    print("Indexando no ChromaDB...")
    indexing_service.index_imoveis(imoveis_salvos)
    
    print(f"Seed concluído! {len(imoveis_salvos)} imóveis processados.")

if __name__ == "__main__":
    main()