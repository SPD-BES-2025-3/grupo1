#!/usr/bin/env python3
"""
Script para comparar como um ID específico está armazenado no MongoDB e ChromaDB
"""
import os
import sys
from pymongo import MongoClient
from bson import ObjectId
import chromadb
import json

def connect_mongodb():
    """Conecta ao MongoDB"""
    mongo_uri = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DATABASE_NAME", "spd_imoveis")
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db.imoveis
    
    return collection

def connect_chromadb():
    """Conecta ao ChromaDB"""
    # Tentar conectar via HTTP primeiro (como na API)
    try:
        client = chromadb.HttpClient(host="localhost", port=7777)
        collection = client.get_or_create_collection(name="imoveis")
        return collection, "HTTP"
    except Exception as e:
        print(f"⚠️ Erro ao conectar via HTTP: {e}")
    
    # Fallback para cliente local (como no integrador)
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="imoveis")
        return collection, "Local"
    except Exception as e:
        print(f"❌ Erro ao conectar localmente: {e}")
        return None, None

def get_mongo_data(collection, imovel_id):
    """Busca dados no MongoDB"""
    try:
        # Tentar buscar por ObjectId
        result = collection.find_one({"_id": ObjectId(imovel_id)})
        if result:
            result["id"] = str(result["_id"])
            del result["_id"]
            return result
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar no MongoDB: {e}")
        return None

def get_chroma_data(collection, imovel_id):
    """Busca dados no ChromaDB"""
    try:
        # Buscar documento específico, incluindo embeddings
        result = collection.get(ids=[imovel_id], include=["embeddings", "metadatas", "documents"])
        
        if result and result.get('ids') and len(result['ids']) > 0:
            print(f"🔍 Debug - Chaves do resultado: {result.keys()}")
            
            # Verificar se há embeddings
            if 'embeddings' in result and result['embeddings']:
                embedding = result['embeddings'][0]
                print(f"🔍 Debug - Tipo do embedding: {type(embedding)}")
                print(f"🔍 Debug - Embedding (primeiros 5): {embedding[:5] if hasattr(embedding, '__getitem__') else 'N/A'}")
                embedding_length = len(embedding) if hasattr(embedding, '__len__') else 0
            else:
                print("🔍 Debug - Sem embeddings no resultado")
                embedding_length = 0
            
            return {
                'id': result['ids'][0],
                'document': result.get('documents', [None])[0],
                'metadata': result.get('metadatas', [None])[0],
                'embedding_length': embedding_length
            }
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar no ChromaDB: {e}")
        return None

def compare_data(imovel_id):
    """Compara dados entre MongoDB e ChromaDB"""
    print(f"🔍 Comparando dados para ID: {imovel_id}")
    print("=" * 80)
    
    # Conectar aos bancos
    mongo_collection = connect_mongodb()
    chroma_collection, chroma_type = connect_chromadb()
    
    if not chroma_collection:
        print("❌ Não foi possível conectar ao ChromaDB")
        return
    
    print(f"✅ Conectado ao MongoDB")
    print(f"✅ Conectado ao ChromaDB ({chroma_type})")
    print()
    
    # Buscar dados no MongoDB
    print("📊 DADOS NO MONGODB:")
    print("-" * 40)
    mongo_data = get_mongo_data(mongo_collection, imovel_id)
    
    if mongo_data:
        print(f"✅ Encontrado no MongoDB")
        print(f"📋 Título: {mongo_data.get('titulo', 'N/A')[:60]}...")
        print(f"📝 Descrição: {mongo_data.get('descricao', 'N/A')[:80]}...")
        print(f"🏗️ Especificações: {len(mongo_data.get('especificacoes', []))} itens")
        print(f"🔑 Campos: {list(mongo_data.keys())}")
    else:
        print("❌ Não encontrado no MongoDB")
    
    print()
    
    # Buscar dados no ChromaDB
    print("🔍 DADOS NO CHROMADB:")
    print("-" * 40)
    chroma_data = get_chroma_data(chroma_collection, imovel_id)
    
    if chroma_data:
        print(f"✅ Encontrado no ChromaDB")
        print(f"🔑 ID: {chroma_data.get('id')}")
        print(f"📄 Document: {chroma_data.get('document', 'N/A')[:80]}...")
        
        metadata = chroma_data.get('metadata', {})
        if metadata:
            print(f"📋 Título (meta): {metadata.get('titulo', 'N/A')[:60]}...")
            print(f"📝 Descrição (meta): {metadata.get('descricao', 'N/A')[:60]}...")
            print(f"🏗️ Especificações (meta): {metadata.get('especificacoes', 'N/A')[:60]}...")
        
        print(f"🧠 Embedding: {chroma_data.get('embedding_length')} dimensões")
    else:
        print("❌ Não encontrado no ChromaDB")
    
    print()
    
    # Comparação
    print("🔄 COMPARAÇÃO:")
    print("-" * 40)
    
    if mongo_data and chroma_data:
        print("✅ Presente em ambos os bancos")
        
        # Comparar conteúdo
        if mongo_data and chroma_data.get('metadata'):
            mongo_titulo = mongo_data.get('titulo', '')
            chroma_titulo = chroma_data['metadata'].get('titulo', '')
            
            if mongo_titulo == chroma_titulo:
                print("✅ Títulos coincidem")
            else:
                print("⚠️ Títulos diferentes:")
                print(f"   MongoDB: {mongo_titulo}")
                print(f"   ChromaDB: {chroma_titulo}")
    
    elif mongo_data and not chroma_data:
        print("⚠️ Presente no MongoDB mas ausente no ChromaDB")
        print("💡 Possível problema de sincronização")
    
    elif not mongo_data and chroma_data:
        print("⚠️ Presente no ChromaDB mas ausente no MongoDB")
        print("💡 Possível inconsistência de dados")
    
    else:
        print("❌ Não encontrado em nenhum dos bancos")

def list_sample_ids():
    """Lista alguns IDs de exemplo"""
    print("📋 Listando alguns IDs de exemplo do MongoDB...")
    
    mongo_collection = connect_mongodb()
    
    # Buscar primeiros 5 documentos
    results = list(mongo_collection.find().limit(5))
    
    if results:
        print("\n🏠 IDs disponíveis para teste:")
        for i, doc in enumerate(results, 1):
            titulo = doc.get('titulo', 'Sem título')[:50]
            print(f"{i}. {str(doc['_id'])} - {titulo}...")
    else:
        print("❌ Nenhum documento encontrado no MongoDB")

def main():
    # Primeiro listar alguns IDs disponíveis
    list_sample_ids()
    print("\n" + "="*80 + "\n")
    
    # ═══════════════════════════════════════════════════════
    # 🔧 CONFIGURAÇÃO: Modifique o ID aqui para comparar
    # ═══════════════════════════════════════════════════════
    IMOVEL_ID = "688e2c8c8f1b9125f01fc58f"  # ID do imóvel final de teste (pós reconstrução)
    
    print(f"🔍 Usando ID específico: {IMOVEL_ID}")
    
    # Verificar se existe no MongoDB
    mongo_collection = connect_mongodb()
    test_doc = mongo_collection.find_one({"_id": ObjectId(IMOVEL_ID)})
    if test_doc:
        print(f"📋 Título: {test_doc.get('titulo', 'N/A')[:50]}...")
    else:
        print("❌ Documento de teste não encontrado no MongoDB")
        return
    
    print()
    compare_data(IMOVEL_ID)
    
    # Adicionar estatísticas gerais
    print("\n" + "="*80 + "\n")
    print("📊 ESTATÍSTICAS GERAIS:")
    print("-" * 40)
    
    # Contar total no MongoDB
    mongo_count = mongo_collection.count_documents({})
    print(f"📦 Total de imóveis no MongoDB: {mongo_count}")
    
    # Contar total no ChromaDB
    chroma_collection, _ = connect_chromadb()
    if chroma_collection:
        try:
            # ChromaDB não tem count direto, vamos fazer uma query
            result = chroma_collection.get()
            chroma_count = len(result['ids']) if result and result.get('ids') else 0
            print(f"🔮 Total de embeddings no ChromaDB: {chroma_count}")
            
            # Verificar sincronização
            if mongo_count == chroma_count:
                print(f"✅ Bancos estão sincronizados!")
            else:
                diff = abs(mongo_count - chroma_count)
                if mongo_count > chroma_count:
                    print(f"⚠️ MongoDB tem {diff} imóveis a mais que ChromaDB")
                else:
                    print(f"⚠️ ChromaDB tem {diff} embeddings a mais que MongoDB")
        except Exception as e:
            print(f"❌ Erro ao contar no ChromaDB: {e}")

if __name__ == "__main__":
    main()