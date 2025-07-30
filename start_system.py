#!/usr/bin/env python3
"""
Script para iniciar todo o sistema SPD Imóveis
- Verifica dependências
- Inicia Worker único
- Inicia API
- Executa testes de verificação
"""
import sys
import os
import time
import subprocess
import signal
import requests
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class SystemStarter:
    def __init__(self):
        self.worker_process = None
        self.api_process = None
        self.streamlit_process = None
        self.base_path = Path(__file__).parent
        
    def check_dependencies(self):
        """Verificar se todas as dependências estão funcionando"""
        print("🔍 Verificando dependências...")
        
        # MongoDB
        try:
            from app.repositories.mongo_repository import MongoRepository
            from app.config import MONGO_URI, MONGO_DB_NAME
            mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
            mongo_repo.get_all_imoveis()
            print("   ✅ MongoDB conectado")
        except Exception as e:
            print(f"   ❌ MongoDB falhou: {e}")
            return False
        
        # Redis
        try:
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            redis_client.ping()
            print("   ✅ Redis conectado (porta 6379)")
        except Exception as e:
            print(f"   ❌ Redis falhou: {e}")
            return False
        
        # ChromaDB
        try:
            from app.repositories.chroma_repository import ChromaRepository
            chroma_repo = ChromaRepository(path="./chroma_db")
            chroma_repo.collection.get()
            print("   ✅ ChromaDB conectado")
        except Exception as e:
            print(f"   ❌ ChromaDB falhou: {e}")
            return False
        
        # Arquivos essenciais
        essential_files = [
            "single_worker.py",
            "main.py",
            "streamlit/app_fixed.py"
        ]
        
        for file_path in essential_files:
            if os.path.exists(self.base_path / file_path):
                print(f"   ✅ {file_path} encontrado")
            else:
                print(f"   ❌ {file_path} não encontrado")
                return False
        
        return True
    
    def start_worker(self):
        """Iniciar o worker único"""
        print("🚀 Iniciando Worker único...")
        try:
            worker_script = self.base_path / "single_worker.py"
            log_file = self.base_path / "worker.log"
            
            # Iniciar worker em background
            with open(log_file, 'w') as f:
                self.worker_process = subprocess.Popen([
                    sys.executable, str(worker_script)
                ], stdout=f, stderr=subprocess.STDOUT, cwd=str(self.base_path))
            
            # Aguardar inicialização
            time.sleep(3)
            
            # Verificar se ainda está rodando
            if self.worker_process.poll() is None:
                print(f"   ✅ Worker iniciado (PID: {self.worker_process.pid})")
                print(f"   📋 Log: {log_file}")
                return True
            else:
                print("   ❌ Worker falhou ao iniciar")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao iniciar worker: {e}")
            return False
    
    def start_api(self):
        """Iniciar a API FastAPI"""
        print("🌐 Iniciando API...")
        try:
            api_port = 8000
            log_file = self.base_path / "api.log"
            
            # Verificar se porta está livre
            try:
                response = requests.get(f"http://localhost:{api_port}/", timeout=2)
                print(f"   ⚠️ API já está rodando na porta {api_port}")
                return True
            except:
                pass  # Porta livre, continuar
            
            # Iniciar API
            with open(log_file, 'w') as f:
                self.api_process = subprocess.Popen([
                    sys.executable, "-m", "uvicorn", "main:app", 
                    "--host", "0.0.0.0", "--port", str(api_port)
                ], stdout=f, stderr=subprocess.STDOUT, cwd=str(self.base_path))
            
            # Aguardar inicialização
            print("   ⏳ Aguardando API inicializar...")
            for i in range(15):  # 15 tentativas = 30 segundos
                try:
                    response = requests.get(f"http://localhost:{api_port}/", timeout=2)
                    if response.status_code == 200:
                        print(f"   ✅ API iniciada (PID: {self.api_process.pid})")
                        print(f"   🔗 URL: http://localhost:{api_port}")
                        print(f"   📋 Log: {log_file}")
                        return True
                except:
                    time.sleep(2)
            
            print("   ❌ API não respondeu em 30 segundos")
            return False
            
        except Exception as e:
            print(f"   ❌ Erro ao iniciar API: {e}")
            return False
    
    def start_streamlit(self):
        """Iniciar o Streamlit"""
        print("📱 Iniciando Streamlit...")
        try:
            streamlit_port = 8501
            log_file = self.base_path / "streamlit.log"
            streamlit_script = self.base_path / "streamlit" / "app_fixed.py"
            
            # Verificar se porta está livre
            try:
                response = requests.get(f"http://localhost:{streamlit_port}", timeout=2)
                print(f"   ⚠️ Streamlit já está rodando na porta {streamlit_port}")
                return True
            except:
                pass  # Porta livre, continuar
            
            # Iniciar Streamlit com caminho completo do venv
            venv_streamlit = self.base_path / "venv" / "bin" / "streamlit"
            with open(log_file, 'w') as f:
                self.streamlit_process = subprocess.Popen([
                    str(venv_streamlit), "run", str(streamlit_script),
                    "--server.port", str(streamlit_port),
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ], stdout=f, stderr=subprocess.STDOUT, cwd=str(self.base_path))
            
            # Aguardar inicialização
            print("   ⏳ Aguardando Streamlit inicializar...")
            for i in range(20):  # 20 tentativas = 40 segundos
                try:
                    response = requests.get(f"http://localhost:{streamlit_port}", timeout=2)
                    if response.status_code == 200:
                        print(f"   ✅ Streamlit iniciado (PID: {self.streamlit_process.pid})")
                        print(f"   🔗 URL: http://localhost:{streamlit_port}")
                        print(f"   📋 Log: {log_file}")
                        return True
                except:
                    time.sleep(2)
            
            print("   ❌ Streamlit não respondeu em 40 segundos")
            return False
            
        except Exception as e:
            print(f"   ❌ Erro ao iniciar Streamlit: {e}")
            return False
    
    def test_system(self):
        """Testar se o sistema está funcionando"""
        print("🧪 Testando sistema...")
        
        # Teste 1: API responde
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("   ✅ API respondendo")
            else:
                print(f"   ❌ API retornou status {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API não responde: {e}")
            return False
        
        # Teste 2: Endpoints principais
        endpoints = [
            ("/imoveis/", "Listar imóveis"),
            ("/search?query=apartamento&n_results=3", "Busca")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {name}")
                else:
                    print(f"   ❌ {name} - Status {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name} - Erro: {e}")
        
        # Teste 3: CRUD rápido
        print("   🔧 Testando CRUD rápido...")
        try:
            # CREATE
            test_data = {
                "titulo": "TESTE SISTEMA INICIADO",
                "descricao": "Imóvel de teste para verificar se sistema está funcionando",
                "especificacoes": ["teste-sistema", "funcionando"]
            }
            
            create_response = requests.post("http://localhost:8000/imoveis/", 
                                          json=test_data, timeout=10)
            if create_response.status_code == 200:
                test_id = create_response.json().get("id")
                print("   ✅ CREATE funcionando")
                
                # Aguardar worker processar
                time.sleep(5)
                
                # Verificar na busca
                search_response = requests.get("http://localhost:8000/search", 
                                             params={"query": "teste sistema iniciado", "n_results": 5})
                if search_response.status_code == 200:
                    results = search_response.json().get("results", [])
                    found = any(r.get("id") == test_id for r in results)
                    if found:
                        print("   ✅ Worker + ChromaDB funcionando")
                    else:
                        print("   ⚠️ Worker pode não estar processando")
                
                # Limpar teste (DELETE)
                delete_response = requests.delete(f"http://localhost:8000/imoveis/{test_id}")
                if delete_response.status_code == 200:
                    print("   ✅ DELETE funcionando")
                
            else:
                print("   ❌ CREATE não funcionando")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro no teste CRUD: {e}")
            return False
        
        return True
    
    def show_status(self):
        """Mostrar status final do sistema"""
        print("")
        print("📊 STATUS DO SISTEMA")
        print("===================")
        
        # Processos
        if self.worker_process and self.worker_process.poll() is None:
            print(f"🔧 Worker: ✅ Rodando (PID: {self.worker_process.pid})")
        else:
            print("🔧 Worker: ❌ Parado")
        
        if self.api_process and self.api_process.poll() is None:
            print(f"🌐 API: ✅ Rodando (PID: {self.api_process.pid})")
        else:
            print("🌐 API: ❌ Parado")
        
        if self.streamlit_process and self.streamlit_process.poll() is None:
            print(f"📱 Streamlit: ✅ Rodando (PID: {self.streamlit_process.pid})")
        else:
            print("📱 Streamlit: ❌ Parado")
        
        # URLs importantes
        print("")
        print("🔗 URLS IMPORTANTES:")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Health: http://localhost:8000/")
        print("   Streamlit: http://localhost:8501")
        
        # Comandos úteis
        print("")
        print("💡 COMANDOS ÚTEIS:")
        print("   Parar sistema: python stop_system.py")
        print("   Reset dados: python reset_and_seed_auto.py")
        print("   Testar CRUD: python test_crud_complete.py")
    
    def setup_signal_handlers(self):
        """Configurar handlers para parar o sistema"""
        def signal_handler(signum, frame):
            print("\n🛑 Parando sistema...")
            self.stop_system()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop_system(self):
        """Parar todos os processos"""
        if self.worker_process:
            try:
                self.worker_process.terminate()
                self.worker_process.wait(timeout=5)
                print("   ✅ Worker parado")
            except:
                self.worker_process.kill()
                print("   ⚠️ Worker forçado a parar")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("   ✅ API parada")
            except:
                self.api_process.kill()
                print("   ⚠️ API forçada a parar")
        
        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
                print("   ✅ Streamlit parado")
            except:
                self.streamlit_process.kill()
                print("   ⚠️ Streamlit forçado a parar")
    
    def run(self):
        """Executar inicialização completa do sistema"""
        print("🚀 INICIANDO SISTEMA SPD IMÓVEIS")
        print("===============================")
        print()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # 1. Verificar dependências
        if not self.check_dependencies():
            print("❌ Falha nas dependências. Sistema não pode iniciar.")
            return False
        
        print()
        
        # 2. Iniciar Worker
        if not self.start_worker():
            print("❌ Falha ao iniciar Worker. Sistema não pode continuar.")
            return False
        
        print()
        
        # 3. Iniciar API
        if not self.start_api():
            print("❌ Falha ao iniciar API. Parando Worker...")
            self.stop_system()
            return False
        
        print()
        
        # 4. Iniciar Streamlit
        if not self.start_streamlit():
            print("⚠️ Falha ao iniciar Streamlit. Sistema funcionará sem interface web.")
        
        print()
        
        # 5. Testar sistema
        if not self.test_system():
            print("⚠️ Alguns testes falharam, mas sistema pode estar funcional.")
        
        # 6. Mostrar status
        self.show_status()
        
        print()
        print("🎉 Sistema iniciado com sucesso!")
        print("   Pressione Ctrl+C para parar o sistema")
        
        # Manter rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            self.stop_system()
        
        return True

if __name__ == "__main__":
    starter = SystemStarter()
    starter.run()