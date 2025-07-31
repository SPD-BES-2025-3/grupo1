import chromadb
import sys

# --- Configurações ---
CHROMA_HOST = 'localhost'
CHROMA_PORT = 7777
# Nome exato da sua coleção
NOME_DA_COLECAO = "imoveis"
# Tamanho do lote para buscar dados para não sobrecarregar a memória.
CHUNK_SIZE = 100

def main():
    """
    Conecta ao ChromaDB e lista todos os itens da coleção 'imoveis'.
    """
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        client.heartbeat()
        print(f"✅ Conectado com sucesso ao ChromaDB em {CHROMA_HOST}:{CHROMA_PORT}\n")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # 1. Acessar a coleção "imoveis" diretamente
        print(f"⬇️  Acessando a coleção: '{NOME_DA_COLECAO}'")
        collection = client.get_collection(name=NOME_DA_COLECAO)
        
        offset = 0
        total_items_processed = 0
        
        # 2. Loop com paginação para buscar todos os itens da coleção
        while True:
            chunk = collection.get(
                limit=CHUNK_SIZE,
                offset=offset,
                include=["metadatas", "documents", "embeddings"]
            )

            if not chunk['ids']:
                # Se não vierem mais IDs, saímos do loop
                break
            
            # 3. Imprimir cada item encontrado no lote
            for i in range(len(chunk['ids'])):
                item_id = chunk['ids'][i]
                item_embedding = chunk['embeddings'][i]
                item_metadata = chunk['metadatas'][i]
                item_document = chunk['documents'][i]

                print(f"\n  ▶️  ID: {item_id}")
                print(f"    Metadados: {item_metadata}")
                print(f"    Documento: {str(item_document)[:200]}...")
                print(f"    Embedding (Dim: {len(item_embedding)}): {str(item_embedding)[:80]}...")

            offset += CHUNK_SIZE
            total_items_processed += len(chunk['ids'])

        print("\n======================================================================")
        print(f"✅ Concluído. Total de {total_items_processed} itens processados na coleção '{NOME_DA_COLECAO}'.")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao processar a coleção '{NOME_DA_COLECAO}': {e}", file=sys.stderr)
        print("   Verifique se a coleção com este nome realmente existe.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()