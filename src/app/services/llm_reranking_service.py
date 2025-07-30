import requests
import json
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMRerankingService:
    def __init__(self, ollama_url: str = None):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", None)
        self.model = "tinyllama:latest"  # Modelo mais leve - 1.1B parâmetros
        self.ollama_enabled = bool(self.ollama_url)
    
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
        # Verificar se Ollama está configurado
        if not self.ollama_enabled or not self.ollama_url:
            logger.info("Ollama não configurado, usando fallback")
            return {
                "decision_reasoning": "IA não configurada - usando seleção automática",
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
                    "temperature": 0.7,
                    "num_predict": 500,  # Limitar resposta para economizar recursos
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # Timeout menor para modelo leve
            )
            
            logger.info(f"Resposta Ollama: status={response.status_code}")
            
            if response.status_code == 200:
                llm_response = response.json()
                parsed_response = self._parse_llm_response(llm_response.get("response", ""))
                
                # Se parse funcionou, retorna o formato estruturado
                if parsed_response and isinstance(parsed_response, dict):
                    return parsed_response
                else:
                    # Fallback se parse falhou
                    return {
                        "decision_reasoning": "Parse da resposta LLM falhou",
                        "should_show_more": True,
                        "selected_properties": self._fallback_ranking(liked_properties, remaining_properties)
                    }
            else:
                logger.error(f"Erro na chamada LLM: {response.status_code}")
                return {
                    "decision_reasoning": "Erro na comunicação com LLM",
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
        Constrói prompt para Gemma3 decidir quais dos 5 restantes mostrar
        """
        prompt = f"""Você é um especialista em recomendação de imóveis. Analise os feedbacks do usuário nos primeiros 5 imóveis e DECIDA quais dos 5 imóveis restantes vale a pena mostrar.

BUSCA ORIGINAL: "{query}"

IMÓVEIS QUE O USUÁRIO CURTIU (dos primeiros 5 mostrados):
"""
        
        for i, prop in enumerate(liked_properties, 1):
            prompt += f"{i}. {prop.get('titulo', 'Sem título')}\n"
            prompt += f"   Descrição: {prop.get('descricao', '')[:100]}...\n"
            prompt += f"   Especificações: {', '.join(prop.get('especificacoes', [])[:3])}\n\n"
        
        prompt += "IMÓVEIS QUE O USUÁRIO REJEITOU (dos primeiros 5 mostrados):\n"
        for i, prop in enumerate(disliked_properties, 1):
            prompt += f"{i}. {prop.get('titulo', 'Sem título')}\n"
            prompt += f"   Descrição: {prop.get('descricao', '')[:100]}...\n"
            prompt += f"   Especificações: {', '.join(prop.get('especificacoes', [])[:3])}\n\n"
        
        prompt += "OS 5 IMÓVEIS RESTANTES (você deve ESCOLHER quais mostrar):\n"
        for i, prop in enumerate(remaining_properties, 1):
            prompt += f"{i}. ID: {prop.get('id')} | {prop.get('titulo', 'Sem título')}\n"
            prompt += f"   Descrição: {prop.get('descricao', '')[:100]}...\n"
            prompt += f"   Especificações: {', '.join(prop.get('especificacoes', [])[:3])}\n\n"
        
        prompt += """TAREFA:
Com base no que o usuário curtiu/rejeitou, SELECIONE apenas os imóveis dos 5 restantes que realmente valem a pena mostrar.
- Se não curtiu nada, seja mais conservador (escolha 1-2 imóveis)
- Se curtiu vários, seja mais generoso (escolha 3-4 imóveis)
- Se rejeitou muitos, evite características similares
- Retorne apenas os IDs dos imóveis que você decidiu mostrar

RESPOSTA (JSON válido):
{
  "decision_reasoning": "Sua análise do padrão de preferência e estratégia de seleção",
  "should_show_more": true/false,
  "selected_properties": [
    {"id": "id_do_imovel_escolhido", "reason": "Por que este imóvel deve ser mostrado"},
    {"id": "outro_id_se_escolhido", "reason": "Justificativa para mostrar este"}
  ]
}"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse da resposta JSON da LLM - retorna o objeto completo
        """
        try:
            # Limpar possível texto extra antes/depois do JSON
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = llm_response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Retornar o objeto completo com decision_reasoning, should_show_more, etc.
                return parsed
            else:
                logger.error("JSON não encontrado na resposta da LLM")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON: {str(e)}")
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