import requests
import os
import subprocess
import time
import logging

logger = logging.getLogger(__name__)

class OllamaHealthService:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.timeout = 5
        
    def is_ollama_running(self) -> bool:
        """Verifica se o Ollama está rodando e acessível."""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_ollama_if_needed(self) -> bool:
        """
        Verifica se o Ollama está rodando, se não estiver tenta iniciar.
        Retorna True se estiver rodando ou foi iniciado com sucesso.
        """
        if self.is_ollama_running():
            logger.info("✅ Ollama já está rodando")
            return True
        
        logger.warning("⚠️ Ollama não está rodando, tentando iniciar...")
        
        try:
            # Tenta iniciar o Ollama
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Aguarda até 30 segundos para o Ollama iniciar
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(1)
                if self.is_ollama_running():
                    logger.info(f"✅ Ollama iniciado com sucesso após {attempt + 1} segundos")
                    return True
                    
            logger.error("❌ Timeout ao aguardar Ollama iniciar")
            return False
            
        except FileNotFoundError:
            logger.error("❌ Comando 'ollama' não encontrado no sistema")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao tentar iniciar Ollama: {str(e)}")
            return False
    
    def get_ollama_status(self) -> dict:
        """Retorna status detalhado do Ollama."""
        running = self.is_ollama_running()
        
        status = {
            "running": running,
            "url": self.ollama_url,
            "models": []
        }
        
        if running:
            try:
                response = requests.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    data = response.json()
                    status["models"] = [model["name"] for model in data.get("models", [])]
            except Exception as e:
                logger.error(f"Erro ao obter modelos Ollama: {str(e)}")
        
        return status