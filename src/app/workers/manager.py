#!/usr/bin/env python3
"""
Gerenciador de Workers - Inicia todos os workers em processos separados
"""
import subprocess
import sys
import os
import signal
import time
from multiprocessing import Process


class WorkerManager:
    def __init__(self):
        self.workers = []
        self.worker_files = [
            "create_worker.py",
            "update_worker.py", 
            "delete_worker.py"
        ]
        
    def start_worker(self, worker_file):
        """Inicia um worker específico"""
        worker_path = os.path.join(os.path.dirname(__file__), worker_file)
        # Definir PYTHONPATH para os imports funcionarem
        env = os.environ.copy()
        src_dir = os.path.join(os.path.dirname(__file__), '../../..')
        env['PYTHONPATH'] = src_dir
        return subprocess.Popen([sys.executable, worker_path], env=env)
    
    def start_all(self):
        """Inicia todos os workers"""
        print("🚀 Iniciando todos os workers...")
        
        for worker_file in self.worker_files:
            try:
                process = self.start_worker(worker_file)
                self.workers.append(process)
                print(f"✅ Worker {worker_file} iniciado (PID: {process.pid})")
            except Exception as e:
                print(f"❌ Erro ao iniciar {worker_file}: {e}")
        
        print(f"\n📊 Total de {len(self.workers)} workers rodando")
        return len(self.workers) > 0
    
    def stop_all(self):
        """Para todos os workers"""
        print("\n🛑 Parando todos os workers...")
        
        for process in self.workers:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Worker PID {process.pid} parado")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Forçando parada do worker PID {process.pid}")
                process.kill()
            except Exception as e:
                print(f"❌ Erro ao parar worker PID {process.pid}: {e}")
        
        self.workers.clear()
        print("🏁 Todos os workers foram parados")
    
    def status(self):
        """Mostra status dos workers"""
        print(f"\n📊 Status dos Workers:")
        
        for i, process in enumerate(self.workers):
            if process.poll() is None:
                print(f"✅ Worker {i+1} (PID {process.pid}): Rodando")
            else:
                print(f"❌ Worker {i+1} (PID {process.pid}): Parado (código: {process.returncode})")
    
    def monitor(self):
        """Monitora workers e reinicia se necessário"""
        print("👁️ Monitor iniciado - Ctrl+C para parar")
        
        try:
            while True:
                # Verificar se algum worker parou
                for i, process in enumerate(self.workers):
                    if process.poll() is not None:
                        print(f"⚠️ Worker {i+1} parou (código: {process.returncode})")
                        print(f"🔄 Reiniciando worker {self.worker_files[i]}...")
                        
                        # Reiniciar worker
                        new_process = self.start_worker(self.worker_files[i])
                        self.workers[i] = new_process
                        print(f"✅ Worker reiniciado (PID: {new_process.pid})")
                
                time.sleep(10)  # Verificar a cada 10 segundos
                
        except KeyboardInterrupt:
            print("\n👋 Monitor interrompido pelo usuário")


def main():
    manager = WorkerManager()
    
    def signal_handler(sig, frame):
        print("\n⚠️ Sinal de interrupção recebido...")
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if manager.start_all():
                manager.monitor()
        elif command == "stop":
            manager.stop_all()
        elif command == "status":
            manager.status()
        else:
            print("Comandos disponíveis: start, stop, status")
    else:
        print("Uso: python manager.py [start|stop|status]")
        print("  start  - Inicia todos os workers e monitora")
        print("  stop   - Para todos os workers")
        print("  status - Mostra status dos workers")


if __name__ == "__main__":
    main()