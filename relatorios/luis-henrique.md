Relatório Individual

Discente: Luís Henrique Alves Rosa  

Entrega 1
Criei o crawler para pegar os anúncios do site 62imoveis em Goiânia - Goiás (Quando fiz o commit o arquivo crawler.py se corrompeu de alguma forma), mas é passível de solução na próxima entrega. UPDATE = O Site mudou o HTML e quebrou meu crawler rs.
Pesquisei sobre camadas de persistências em Banco de Dados Vetoriais. Como essas camdas ainda não existem como em bancos tradicionais (ORMs, ODMs), optaremos por criar um mistura entre nossa prórpia implementação híbrida com a biblioteca llamaindex (o que requer um pouco de buscas não convencionais)

Adicionei um template para o serviço de indexação para chamar o serviço de geração de embeddings.


Como o tema sobre bancos de dados vetoriais é muito novo, o projeto pode passar por algumas alterações até a entrega final.
Além disso, devido a natureza nichada desse tipo de banco de dados em um projetos de IA, alguns colegas nunca trabalharam com esse tipo de aplicação, o que requer um certo tempo para a absorção desse conhecimento por parte deles.

O template do projeto juntamente com os diagramas da aplicação está pronto, acredito que vamos conseguir entregar esse projeto até o final da disciplina.

Não tive tempo o suficiente durante o final de semana para criar a camada de persistência para o MongoDB, mas não é uma coisa complicada de implementar para a próxima entrega.

Entrega 2

Realizei a implementação do chroma_repository e do serviço de busca. Além disso, fiquei responsável por dockerizar a aplicação, o que se mostrou um certo desafio, pois o ollama que é nosso serviço de llm não funcionava de jeito nenhum. Logo, decidimos por manter uma versão local dele e aí sim o projeto funcionou.
OBS: O colega Pedro Campos ajudou nessa parte do ollama.






