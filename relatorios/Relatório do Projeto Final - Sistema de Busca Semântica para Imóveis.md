# **Relatório do Projeto Final \- Sistema de Busca Semântica para Imóveis**

## **Membros da Equipe**

| Nome | Função Principal |
| ----- | ----- |
| Luís Henrique | Processamento Semântico |
| Matheus Lucas | Backend e Integração |
| Wilson Gomes | Frontend (UI/UX) |
| Juliano Kenzo | Banco de Dados |
| Pedro Melo | Vetorização e Busca |

## **Seção 1 \- Introdução**

A busca por imóveis para compra ou aluguel é um processo que pode ser demorado e ineficiente, especialmente quando as ferramentas tradicionais exigem que o usuário filtre manualmente por categorias fixas. Com o avanço da inteligência artificial surge a possibilidade de criar aplicações mais intuitivas que compreendem melhor a intenção do usuário.

Este projeto propõe o desenvolvimento de uma aplicação web capaz de interpretar buscas semânticas do usuário e retornar imóveis disponíveis para compra ou aluguel com base na similaridade de significado, e não apenas em palavras-chave exatas.

A motivação é oferecer uma experiência de busca mais natural e eficiente para os usuários, utilizando tecnologias modernas de aprendizado de máquina, bancos de dados vetoriais e bancos orientados a documentos.

## **Seção 2 \- Plano**

### **Objetivo Geral**

Desenvolver uma aplicação web que responde a requisições semânticas com imóveis disponíveis para compra ou aluguel.

### **Objetivos Específicos**

* Permitir que o usuário faça uma busca por imóveis em linguagem natural.

* Interpretar a intenção do usuário utilizando embeddings de linguagem.

* Buscar o imóvel mais similar em um banco de dados vetorial.

* Recuperar os dados reais do imóvel a partir de um banco de dados orientado a documentos.

### **Tecnologias e Ferramentas**

* **Frontend:** Python (Streamlit)

* **Backend:** Python (FastAPI)

* **Banco Vetorial:**  Chroma DB

* **Banco de Documentos:** MongoDB

* **Linguagem Natural:** Sentence-BERT (SBERT)

* **Controle de Versão:** Git \+ GitHub

* **Testes unitários:** Pytest

## **Seção 3 \- Divisão de Tarefas**

| Tarefa | Responsável | Prazo | Descrição |
| ----- | ----- | ----- | ----- |
| Definição do layout e protótipo UI | Equipe Frontend | 01/08/2025 | Criar wireframes e layout inicial |
| Implementação do frontend (React) | Equipe Frontend | 15/08/2025 | Componentes e integração API |
| Configuração do backend (FastAPI) | Equipe Backend | 01/08/2025 | Endpoints, autenticação |
| Geração de embeddings e busca vetorial | Equipe IA | 10/08/2025 | Embeddings com SBERT \+ FAISS |
| Integração com MongoDB | Equipe Backend | 15/08/2025 | Busca e estrutura de dados |
| Testes unitários com JUnit (caso Java) | Equipe Backend | 20/08/2025 | Classes de domínio e repositórios |

## **Seção 4 \- Modelagem Inicial** Disponível no github

## **Seção 5 \- Documentação de Código Inicial**

### A documentação está disponível aqui https://github.com/SPD-BES-2025-3/grupo1

## **Seção 6 \- Testes Unitários**

### Todos os testes desenvolvidos estão disponíveis aqui (link do github). Para executar os testes siga a documentação da seção anterior.

