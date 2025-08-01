# Relatório Individual
**Discente: Matheus Lucas Morais Pires**  

## Entrega 1  
Criei a classe CidadeRepository que faz a interface entre a coleção de cidades do MongoDB e o model de Cidade, esse repositório permite as operações de CREATE e READ.Também criei a classe SearchService que é responsável por executar a busca semântica no banco vetorial e hidratar os dados com as informações vindas do MongoDB. Por fim criei os primeiros testes automátizado, mais específicamente dois, um que testa todo o processo de busca por similaridade do ínicio ao fim, e outro que busca algo que não existe no banco vetorial, garantindo que nesse caso, o sistema retorne uma lista vazia.

Nessa experiência nessa primeira entrega do projeto foi tranquila, especialmente porque não trabalhei diretamente com a parte de embedding que é a parte mais difícil do projeto, mesmo assim gostei muito de cuidar dos testes automatizado, já havia estudados testes teoricamente mas é a primeira vez que realmente tive que desenvolver testes pensando n corretude do projeto.

## Entrega 2
Na segunda entrega do trabalho eu fiquei responsável pelos modelos de imóvel e de cidade, (cada imóvel tem uma cidade). Além dos modelos também fiquei reponsável pelo repositório do mongodb que faz a interface entre nossa aplicação e as coleções do banco, também criei os endpoints da nossa API relacionados a essas entidades, assim como integrei eles com o frontend. Criei testes automatizados para testar tanto o repositório do MongoDB quanto a nossa API REST. Também ajudei a dockerizar nosso projeto para facilitar a execução em diferentes ambientes. E por fim fiquei responsável por implementar a integração entre os bancos (Mongo e Chroma) utilizando Redis + PubSub como foi sugerido pelo professor durante a apresentação do nosso grupo.




