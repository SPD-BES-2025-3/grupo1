Relatório Individual

Discente: Juliano Kenzo Watanabe Santana

**Entrega 1**

Nunca tive contato com bancos vetoriais, portanto a implementação dos métodos podem estar levemente ineficiente.

Inicialmente para o main.py, cria-se uma instância do FastAPI. Em seguida, implementei um roteamento incluindo os endpoints. Por fim adicionei um endpoint raiz para verificação de status da API.

Em generic_articles.py, criei o endpoint POST para criação de anúncios de imóveis. Implementei a integração com serviço de indexação que automaticamente salva o anúncio, gera um vetor do conteúdo e indexa o documento.

Para a instanciação de serviços em dependencies.py, criei repositórios para diferentes objetos:
* AnuncioRepository - gerenciamento de anúncios
* CidadeRepository - dados de cidades
* ImobiliariaRepository - informações de imobiliárias

Configurei serviços principais:
* IndexingService - indexação e geração de embeddings
* SearchService - busca semântica

Todos os métodos foram integrados com MongoDB e banco de dados vetorial.

**Entrega 2**

Criei a classe MongoRepository, que gerencia automaticamente todas as operações CRUD para imóveis, corretores e cidades - incluindo a conversão entre ObjectIds e strings para maior compatibilidade.

Implementei endpoints RESTful para cada entidade nos routers, garantindo validações robustas em criação, leitura, atualização e exclusão. Nos imóveis adicionei endpoints especializados para sincronização com o ChromaDB.

Auxiliei na parte do search.py na busca semântica que transforma consultas em embeddings, pesquisa similaridades no ChromaDB e mantém um fallback para busca tradicional.
