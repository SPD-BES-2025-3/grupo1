#!/usr/bin/env python3
"""
Script para parar todo o sistema SPD Imóveis
"""
import subprocess
import sys
import time

def stop_processes():
    """Parar todos os processos do sistema"""
    print("🛑 PARANDO SISTEMA SPD IMÓVEIS")
    print("=============================")
    
    processes_to_stop = [
        ("single_worker.py", "Worker"),
        ("uvicorn main:app", "API"),
        ("streamlit run", "Streamlit")
    ]
    
    stopped_count = 0
    
    for process_name, display_name in processes_to_stop:
        print(f"🔍 Procurando {display_name}...")
        
        try:
            # Encontrar processos
            result = subprocess.run([
                "pgrep", "-f", process_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                pids = [pid for pid in pids if pid]  # Remover strings vazias
                
                if pids:
                    print(f"   📋 Encontrados {len(pids)} processo(s): {', '.join(pids)}")
                    
                    # Parar processos
                    for pid in pids:
                        try:
                            subprocess.run(["kill", pid], check=True)
                            print(f"   ✅ {display_name} (PID: {pid}) parado")
                            stopped_count += 1
                        except:
                            try:
                                subprocess.run(["kill", "-9", pid], check=True)
                                print(f"   ⚠️ {display_name} (PID: {pid}) forçado a parar")
                                stopped_count += 1
                            except:
                                print(f"   ❌ Falha ao parar {display_name} (PID: {pid})")
                else:
                    print(f"   ℹ️ {display_name} não está rodando")
            else:
                print(f"   ℹ️ {display_name} não está rodando")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar {display_name}: {e}")
    
    print()
    print(f"📊 RESULTADO: {stopped_count} processo(s) parado(s)")
    
    if stopped_count > 0:
        print("⏳ Aguardando 2 segundos para processos terminarem...")
        time.sleep(2)
        print("✅ Sistema parado com sucesso!")
    else:
        print("ℹ️ Nenhum processo do sistema estava rodando")
    
    print()
    print("💡 Para iniciar novamente:")
    print("   python start_system.py")

if __name__ == "__main__":
    stop_processes()