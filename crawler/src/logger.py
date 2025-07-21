from loguru import logger
import sys
import os

def setup_logger(log_file: str = "logs/crawler.log"):
    # Cria o diretório de logs, se não existir
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Remove o logger padrão do Loguru
    logger.remove()
    
    # Adiciona o logger para o console com formatação colorida e nível INFO
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Adiciona o logger para arquivo com rotação, retenção e compressão
    logger.add(
        sys.stdout,
        # rotation="10 MB",   # Roda o log a cada 10 MB
        # retention="10 days", # Mantém os logs por 10 dias
        # compression="zip",   # Compacta os logs antigos
        level="DEBUG"
    )