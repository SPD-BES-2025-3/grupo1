import requests
import json
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMRerankingService:
    def __init__(self, ollama_url: str = None):
        # Priorizar URL passada, depois env var, depois URL padrão do docker-compose
        # Dentro do container Docker, usar o nome do serviço; fora, usar localhost
        default_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        if not default_url.startswith("http"):
            default_url = "http://localhost:11435"  # Fallback para desenvolvimento local
            
        self.ollama_url = ollama_url or default_url
        self.model = "gemma3:4b"  # Modelo mais moderno e eficiente para JSON estruturado
        self.ollama_enabled = True  # Sempre tentar usar o Ollama
        
        # Importar aqui para evitar dependência circular
        from .ollama_health_service import OllamaHealthService
        self.ollama_health = OllamaHealthService()
    
    def rerank_properties(
        self, 
        query: str, 
        liked_properties: List[Dict[str, Any]], 
        disliked_properties: List[Dict[str, Any]], 
        remaining_properties: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Re-ranking usando LLM com base no feedback do usuário
        """
        # Verificar se Ollama está configurado e rodando
        if not self.ollama_enabled or not self.ollama_url:
            logger.info("Ollama não configurado, usando fallback")
            return {
                "decision_reasoning": "IA não configurada - usando seleção automática",
                "should_show_more": True,
                "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
            }
        
        logger.info(f"Usando Ollama em: {self.ollama_url}")
        
        # Verificar se o serviço está acessível
        try:
            test_response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if test_response.status_code != 200:
                logger.warning(f"Ollama não acessível em {self.ollama_url}, usando fallback")
                return {
                    "decision_reasoning": "Ollama não acessível - usando seleção automática",
                    "should_show_more": True,
                    "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
                }
        except Exception as e:
            logger.warning(f"Erro ao conectar com Ollama: {e}, usando fallback")
            return {
                "decision_reasoning": "Erro de conexão com Ollama - usando seleção automática",
                "should_show_more": True,
                "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
            }
        
        # Tentar iniciar Ollama se não estiver rodando
        if not self.ollama_health.start_ollama_if_needed():
            logger.warning("Ollama não pôde ser iniciado, usando fallback")
            return {
                "decision_reasoning": "Ollama indisponível - usando seleção automática",
                "should_show_more": True,
                "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
            }
        
        try:
            prompt = self._build_prompt(query, liked_properties, disliked_properties, remaining_properties)
            logger.info(f"Enviando prompt para {self.model} com {len(prompt)} caracteres")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Muito determinístico para JSON
                    "num_predict": 400,  # Maior para permitir JSON completo
                    "top_p": 0.9,
                    "num_ctx": 4096  # Contexto adequado para Gemma3
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # Timeout muito maior para Gemma3 4B (modelo pesado)
            )
            
            logger.info(f"Resposta Ollama: status={response.status_code}, URL={self.ollama_url}")
            
            if response.status_code == 200:
                llm_response = response.json()
                raw_response = llm_response.get("response", "")
                logger.info(f"Resposta LLM bruta: {raw_response[:200]}...")
                
                parsed_response = self._parse_llm_response(raw_response)
                
                # Se parse funcionou, retorna o formato estruturado
                if parsed_response and isinstance(parsed_response, dict):
                    logger.info("Parse da resposta LLM bem-sucedido")
                    return parsed_response
                else:
                    # Fallback se parse falhou
                    logger.warning(f"Parse falhou. Resposta: {raw_response[:500]}")
                    return {
                        "decision_reasoning": "Parse da resposta LLM falhou",
                        "should_show_more": True,
                        "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
                    }
            else:
                logger.error(f"Erro na chamada LLM: {response.status_code}, texto: {response.text}")
                return {
                    "decision_reasoning": f"Erro na comunicação com LLM: {response.status_code}",
                    "should_show_more": True,
                    "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
                }
                
        except Exception as e:
            logger.error(f"Erro no re-ranking LLM: {str(e)}")
            return {
                "decision_reasoning": f"Erro no sistema: {str(e)}",
                "should_show_more": True,
                "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
            }
    
    def _build_prompt(
        self, 
        query: str, 
        liked_properties: List[Dict[str, Any]], 
        disliked_properties: List[Dict[str, Any]], 
        remaining_properties: List[Dict[str, Any]]
    ) -> str:
        """
        Constrói prompt simplificado para TinyLlama
        """
        prompt = f"""Você é um especialista em recomendação de imóveis. Analise as opções e selecione os melhores imóveis.

BUSCA: {query}

IMÓVEIS CURTIDOS:
"""
        
        if liked_properties:
            for prop in liked_properties:
                prompt += f"- {prop.get('titulo', 'Sem título')[:60]}\n"
        else:
            prompt += "- Nenhum ainda\n"
        
        prompt += "\nIMÓVEIS REJEITADOS:\n"
        if disliked_properties:
            for prop in disliked_properties:
                prompt += f"- {prop.get('titulo', 'Sem título')[:60]}\n"
        else:
            prompt += "- Nenhum ainda\n"
        
        prompt += "\nOPÇÕES RESTANTES:\n"
        for i, prop in enumerate(remaining_properties, 1):
            title = prop.get('titulo', 'Sem título')[:50]
            desc = prop.get('descricao', '')[:80]
            prompt += f"{i}. ID: {prop.get('id')}\n   Título: {title}\n   Descrição: {desc}\n\n"
        
        prompt += """Com base nas preferências demonstradas, selecione os melhores imóveis das opções restantes.

RESPONDA APENAS COM JSON VÁLIDO:
{
  "selected_properties": [
    {"id": "id_do_imovel", "reason": "Motivo da seleção"}
  ]
}"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse da resposta JSON da LLM - retorna o objeto completo
        """
        try:
            # Remover markdown se presente (```json...```)
            clean_response = llm_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.startswith('```'):
                clean_response = clean_response[3:]   # Remove ```
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]  # Remove ```
            
            # Tentar encontrar JSON na resposta limpa
            start_idx = clean_response.find('{')
            end_idx = clean_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = clean_response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Verificar se tem a estrutura básica
                if "selected_properties" in parsed:
                    return {
                        "decision_reasoning": "Resposta processada com sucesso pelo LLM",
                        "should_show_more": True,
                        "selected_properties": parsed["selected_properties"]
                    }
                else:
                    logger.error("JSON válido mas sem 'selected_properties'")
                    return {}
            else:
                logger.error("JSON não encontrado na resposta da LLM")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON: {str(e)}")
            logger.error(f"Resposta bruta que falhou: {llm_response}")
            return {}
    
    def _fallback_ranking(
        self, 
        liked_properties: List[Dict[str, Any]], 
        remaining_properties: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fallback simples se LLM falhar - retorna estratégia conservadora
        """
        # Se curtiu algo, mostra 2-3 imóveis restantes
        # Se não curtiu nada, mostra apenas 1
        num_to_show = min(2 if liked_properties else 1, len(remaining_properties))
        
        fallback_results = []
        for i, prop in enumerate(remaining_properties[:num_to_show]):
            fallback_results.append({
                "id": prop.get("id"),
                "reason": "Fallback conservador - LLM indisponível"
            })
        
        return fallback_results