import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List

# Configurações do backend
import os
FASTAPI_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

st.set_page_config(page_title="SPD Imóveis", page_icon="🏠", layout="wide")

def get_preview_imoveis() -> List[Dict[str, Any]]:
    """Busca 5 imóveis de preview"""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/imoveis/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[:5]  # Primeiros 5 imóveis
            return []
        return []
    except requests.exceptions.ConnectionError:
        st.error("🔌 Erro de conexão com a API")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ A API está demorando para responder")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao buscar imóveis: {str(e)}")
        return None

def display_imovel_card(imovel: Dict[str, Any], index: int = 0):
    """Exibe um cartão do imóvel"""
    imovel_id = imovel.get('id', f'imovel_{index}')
    unique_key = f"detail_{imovel_id}_{index}"
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(imovel.get('titulo', 'Sem título'))
            st.write(f"**ID:** {imovel.get('id', 'N/A')}")
            
            descricao = imovel.get('descricao', '')
            if len(descricao) > 150:
                descricao = descricao[:150] + "..."
            st.write(descricao)
            
            specs = imovel.get('especificacoes', [])
            if specs:
                st.write("**Especificações:**")
                for spec in specs[:3]:  
                    st.write(f"• {spec}")
                if len(specs) > 3:
                    st.write(f"... e mais {len(specs) - 3} especificações")
        
        with col2:
            if st.button("🔍 Ver Detalhes", key=unique_key):
                st.session_state.selected_imovel = imovel
                st.rerun()
        
        st.divider()

def main():
    st.title("🏠 SPD Imóveis - Sistema Inteligente")
    
   
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Escolha uma página:", ["🏠 Preview", "💬 Chat", "⚙️ Gerenciar Imóveis", "🕷️ Crawler", "👔 Corretores", "🏙️ Cidades"])
    
    if page == "🏠 Preview":
        st.header("📋 Preview dos Imóveis")
        st.write("Aqui estão os 5 primeiros imóveis cadastrados:")
        
        imoveis = get_preview_imoveis()
        
        if imoveis is None:
            st.info("💡 Certifique-se de que a API está rodando:")
            st.code("python -m uvicorn main:app --host 0.0.0.0 --port 8001")
        elif imoveis:
            for index, imovel in enumerate(imoveis):
                display_imovel_card(imovel, index)
        else:
            st.info("📭 Nenhum imóvel cadastrado ainda.")
            st.write("Use a aba **Gerenciar Imóveis** ou **Crawler** para adicionar novos imóveis.")
    
    elif page == "💬 Chat":
        st.header("💬 Chat com Busca Inteligente")
        
        # Inicializar estados da sessão
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_results" not in st.session_state:
            st.session_state.current_results = []
        if "remaining_results" not in st.session_state:
            st.session_state.remaining_results = []
        if "current_query" not in st.session_state:
            st.session_state.current_query = ""
        if "feedbacks" not in st.session_state:
            st.session_state.feedbacks = {}
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Procure por imóveis... (ex: apartamento 3 quartos)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Buscando imóveis..."):
                    try:
                        search_response = requests.get(
                            f"{FASTAPI_BASE_URL}/search",
                            params={"query": prompt, "n_results": 30} 
                        )
                        
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            all_results = search_data.get('results', [])
                            
                            if all_results:
                                shown_results = all_results[:5]
                                remaining_results = all_results[5:] 
                                
                                st.session_state.current_results = shown_results
                                st.session_state.remaining_results = remaining_results  
                                st.session_state.current_query = prompt
                                st.session_state.feedbacks = {} 
                                
                                response_text = f"Encontrei **{len(shown_results)}** imóveis principais (de {len(all_results)} total):\n\n"
                                
                                for i, imovel in enumerate(shown_results, 1):
                                    response_text += f"**{i}. {imovel.get('titulo', 'Sem título')}**\n"
                                    response_text += f"📍 **ID:** {imovel.get('id', 'N/A')}\n"
                                    
                                    desc = imovel.get('descricao', '')
                                    if len(desc) > 100:
                                        desc = desc[:100] + "..."
                                    response_text += f"📝 {desc}\n"
                                    
                                    specs = imovel.get('especificacoes', [])
                                    if specs:
                                        response_text += f"🏗️ **Especificações:** {', '.join(specs[:2])}"
                                        if len(specs) > 2:
                                            response_text += f" e mais {len(specs) - 2}..."
                                    response_text += "\n\n"
                                
                                response_text += "👆 **Avalie os imóveis acima e clique em 'Melhorar Busca' para resultados personalizados!**"
                            else:
                                response_text = "😔 Não encontrei imóveis com essas características. Tente termos como 'apartamento', 'casa', '3 quartos', etc."
                        else:
                            response_text = "❌ Erro na busca. Verifique se a API está funcionando."
                    
                    except requests.exceptions.ConnectionError:
                        response_text = "🔌 Não foi possível conectar ao servidor. Certifique-se de que a API está rodando na porta 8001."
                    
                    except Exception as e:
                        response_text = f"❌ Erro inesperado: {str(e)}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        if st.session_state.current_results:
            st.markdown("---")
            st.subheader("🎯 Sistema de Feedback Inteligente")
            st.markdown("**Avalie os imóveis acima para melhorar suas próximas recomendações:**")
            
            for i, imovel in enumerate(st.session_state.current_results):
                imovel_id = imovel.get('id', f'imovel_{i}')
                
                col1, col2, col3 = st.columns([6, 1, 1])
                
                with col1:
                    st.write(f"**{i+1}. {imovel.get('titulo', 'Sem título')}** (ID: {imovel_id})")
                    st.caption(f"{imovel.get('descricao', '')[:80]}...")
                
                with col2:
                    if st.button("👍", key=f"like_{imovel_id}", help="Curtir este imóvel"):
                        st.session_state.feedbacks[imovel_id] = "like"
                        st.success("Feedback registrado!")
                        st.rerun()
                
                with col3:
                    if st.button("👎", key=f"dislike_{imovel_id}", help="Não curtir este imóvel"):
                        st.session_state.feedbacks[imovel_id] = "dislike"
                        st.error("Feedback registrado!")
                        st.rerun()
                
                current_feedback = st.session_state.feedbacks.get(imovel_id)
                if current_feedback:
                    emoji = "👍" if current_feedback == "like" else "👎"
                    st.write(f"Seu feedback: {emoji}")
                
                st.divider()
            
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                if st.button("🚀 Melhorar Busca com IA", type="primary", use_container_width=True):
                    if st.session_state.feedbacks:
                        with st.spinner("🤖 Analisando seus gostos com Gemma3..."):
                            try:
                                liked_properties = [
                                    imovel for imovel in st.session_state.current_results 
                                    if st.session_state.feedbacks.get(imovel.get('id')) == "like"
                                ]
                                disliked_properties = [
                                    imovel for imovel in st.session_state.current_results 
                                    if st.session_state.feedbacks.get(imovel.get('id')) == "dislike"
                                ]
                                
                                rerank_data = {
                                    "query": st.session_state.current_query,
                                    "liked_properties": liked_properties,
                                    "disliked_properties": disliked_properties,
                                    "remaining_properties": st.session_state.remaining_results
                                }
                                
                                rerank_response = requests.post(
                                    f"{FASTAPI_BASE_URL}/rerank/",
                                    json=rerank_data
                                )
                                
                                if rerank_response.status_code == 200:
                                    rerank_result = rerank_response.json()
                                    selected_results = rerank_result.get('reranked_results', [])
                                    
                                    if selected_results:
                                        refined_text = f"🤖 **IA analisou seus gostos e SELECIONOU {len(selected_results)} imóveis dos restantes:**\n\n"
                                        
                                        for i, imovel in enumerate(selected_results, 1):
                                            refined_text += f"**{i}. {imovel.get('titulo', 'Sem título')}**\n"
                                            refined_text += f"📍 **ID:** {imovel.get('id', 'N/A')}\n"
                                            refined_text += f"🧠 **Por que a IA escolheu:** {imovel.get('llm_reason', 'Selecionado baseado em seus gostos')}\n"
                                            
                                            desc = imovel.get('descricao', '')
                                            if len(desc) > 100:
                                                desc = desc[:100] + "..."
                                            refined_text += f"📝 {desc}\n\n"
                                        
                                        decision_reasoning = rerank_result.get('decision_reasoning', '')
                                        if decision_reasoning:
                                            refined_text += f"🎯 **Estratégia da IA:** {decision_reasoning}\n\n"
                                        
                                        refined_text += f"💡 A IA decidiu mostrar apenas {len(selected_results)} dos 5 imóveis restantes baseado no seu perfil de preferências."
                                        
                                        st.session_state.messages.append({
                                            "role": "assistant", 
                                            "content": refined_text
                                        })
                                        
                                        st.session_state.feedbacks = {}
                                        st.session_state.current_results = selected_results
                                        st.session_state.remaining_results = []
                                        
                                        st.success("✅ IA selecionou os melhores imóveis para você!")
                                        st.rerun()
                                    else:
                                        st.info("🤖 A IA analisou os imóveis restantes mas decidiu que nenhum se adequa ao seu perfil de preferências.")
                                else:
                                    st.error("❌ Erro na API de re-ranking")
                                    
                            except Exception as e:
                                st.error(f"❌ Erro no re-ranking: {str(e)}")
                    else:
                        st.warning("⚠️ Avalie pelo menos um imóvel antes de melhorar a busca!")
    
    elif page == "⚙️ Gerenciar Imóveis":
        st.header("⚙️ Gerenciar Imóveis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Adicionar", "📋 Listar", "✏️ Editar", "🗑️ Excluir"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col2:
                if st.button("🎲 Adicionar Imóveis de Teste", type="secondary", use_container_width=True):
                    with st.spinner("Gerando e inserindo imóveis de teste..."):
                        import random
                        
                        bairros = ["Centro", "Jardim América", "Setor Bueno", "Setor Marista", "Setor Oeste", 
                                  "Setor Sul", "Jardim Goiás", "Setor Nova Suíça", "Alphaville", "Park Lozandes",
                                  "Setor Coimbra", "Setor Pedro Ludovico", "Vila Nova", "Setor Universitário",
                                  "Jardim Europa", "Setor Aeroporto", "Parque Amazônia", "Cidade Jardim",
                                  "Setor Negrão de Lima", "Alto da Glória", "Setor Leste Vila Nova", "Jardim Novo Mundo"]
                        tipos = ["Apartamento", "Casa", "Casa de Condomínio", "Cobertura", "Kitnet", "Loft",
                                "Flat", "Studio", "Duplex", "Triplex"]
                        
                        success_count = 0
                        total_imoveis = 100  # Criar 100 imóveis de teste para ter uma base robusta
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(total_imoveis):
                            tipo = random.choice(tipos)
                            bairro = random.choice(bairros)
                            if tipo == "Kitnet":
                                quartos = 1
                                area = random.randint(25, 45)
                                preco = random.randint(800, 2000)
                            elif tipo == "Loft":
                                quartos = 1
                                area = random.randint(35, 70)
                                preco = random.randint(1500, 3500)
                            elif tipo == "Apartamento":
                                quartos = random.randint(2, 4)
                                area = random.randint(60, 150)
                                preco = random.randint(1800, 6000)
                            elif tipo == "Casa":
                                quartos = random.randint(2, 5)
                                area = random.randint(100, 300)
                                preco = random.randint(2000, 8000)
                            elif tipo == "Cobertura":
                                quartos = random.randint(3, 4)
                                area = random.randint(150, 400)
                                preco = random.randint(5000, 15000)
                            elif tipo == "Casa de Condomínio":
                                quartos = random.randint(3, 5)
                                area = random.randint(150, 350)
                                preco = random.randint(3500, 10000)
                            elif tipo == "Flat":
                                quartos = 1
                                area = random.randint(30, 50)
                                preco = random.randint(1200, 2500)
                            elif tipo == "Studio":
                                quartos = 1
                                area = random.randint(25, 40)
                                preco = random.randint(900, 1800)
                            elif tipo == "Duplex":
                                quartos = random.randint(2, 4)
                                area = random.randint(120, 250)
                                preco = random.randint(3000, 7000)
                            else:  # Triplex
                                quartos = random.randint(3, 5)
                                area = random.randint(200, 450)
                                preco = random.randint(4500, 12000)
                            
                            especificacoes = [
                                f"R$ {preco:,.2f}",
                                f"{area}m²",
                                f"{quartos} quartos",
                                f"{random.randint(1, 3)} banheiros",
                                f"{random.randint(0, 2)} vagas"
                            ]
                            
                            caracteristicas_possiveis = [
                                "Piscina", "Churrasqueira", "Academia", "Salão de festas", 
                                "Playground", "Portaria 24h", "Elevador", "Varanda gourmet",
                                "Área de serviço", "Despensa", "Home office", "Ar condicionado"
                            ]
                            caracteristicas_selecionadas = random.sample(caracteristicas_possiveis, k=random.randint(3, 6))
                            especificacoes.extend(caracteristicas_selecionadas)
                            
                            payload = {
                                "titulo": f"{tipo} no {bairro} - {quartos} quartos",
                                "descricao": f"Excelente {tipo.lower()} localizado no {bairro}, em Goiânia. "
                                           f"Imóvel com {area}m² de área total, {quartos} quartos, em ótimo estado de conservação. "
                                           f"Próximo a escolas, supermercados e com fácil acesso às principais vias da cidade. "
                                           f"Ideal para quem busca conforto e praticidade. Agende sua visita!",
                                "especificacoes": especificacoes
                            }
                            
                            try:
                                response = requests.post(f"{FASTAPI_BASE_URL}/imoveis/", json=payload)
                                if response.status_code == 200:
                                    success_count += 1
                            except:
                                pass
                            
                            progress = (i + 1) / total_imoveis
                            progress_bar.progress(progress)
                            status_text.text(f"Processando: {i + 1}/{total_imoveis} imóveis...")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if success_count > 0:
                            st.success(f"✅ {success_count} imóveis de teste adicionados com sucesso!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao adicionar imóveis de teste")
            
            def ad_form():
                mode = "Editar" if st.session_state.get('selected_ad') is not None else "Criar"

                with st.form(key="ad_form"):
                    st.subheader(f"{mode} Imóvel")

                    initial = {}
                    if st.session_state.get('selected_ad') is not None:
                        try:
                            response = requests.get(f"{FASTAPI_BASE_URL}/imoveis/")
                            if response.status_code == 200:
                                imoveis = response.json()
                                if st.session_state.selected_ad < len(imoveis):
                                    initial = imoveis[st.session_state.selected_ad]
                        except:
                            pass

                    titulo = st.text_input("Título", value=initial.get('titulo', ''))
                    descricao = st.text_area("Descrição", value=initial.get('descricao', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        preco = st.number_input(
                            "Preço (R$)", min_value=0.0, step=50.0,
                            value=initial.get('preco', 0.0)
                        )
                        area = st.number_input(
                            "Área (m²)", min_value=0.0, step=1.0,
                            value=initial.get('area', 0.0)
                        )
                        quartos = st.number_input(
                            "Quartos", min_value=0, step=1,
                            value=initial.get('quartos', 0)
                        )
                    
                    with col2:
                        banheiros = st.number_input(
                            "Banheiros", min_value=0, step=1,
                            value=initial.get('banheiros', 0)
                        )
                        suites = st.number_input(
                            "Suítes", min_value=0, step=1,
                            value=initial.get('suites', 0)
                        )
                        vagas = st.number_input(
                            "Vagas garagem", min_value=0, step=1,
                            value=initial.get('vagas', 0)
                        )
                    
                    caracteristicas = st.text_area(
                        "Características adicionais (separadas por vírgula)",
                        value=", ".join(initial.get('especificacoes', [])),
                        placeholder="piscina, churrasqueira, jardim, portaria 24h"
                    )

                    if st.form_submit_button(f"✅ {mode} Imóvel"):
                        if not titulo or not descricao:
                            st.error("⚠️ Título e descrição são obrigatórios!")
                            return
                        
                        specs = []
                        if preco > 0:
                            specs.append(f"R$ {preco:,.2f}")
                        if area > 0:
                            specs.append(f"{area}m²")
                        if quartos > 0:
                            specs.append(f"{quartos} quartos")
                        if banheiros > 0:
                            specs.append(f"{banheiros} banheiros")
                        if suites > 0:
                            specs.append(f"{suites} suítes")
                        if vagas > 0:
                            specs.append(f"{vagas} vagas")
                        
                        if caracteristicas.strip():
                            extras = [c.strip() for c in caracteristicas.split(",") if c.strip()]
                            specs.extend(extras)
                        
                        payload = {
                            "titulo": titulo,
                            "descricao": descricao,
                            "especificacoes": specs
                        }
                        
                        try:
                            if st.session_state.get('selected_ad') is None:
                                response = requests.post(f"{FASTAPI_BASE_URL}/imoveis/", json=payload)
                            else:
                                response = requests.post(f"{FASTAPI_BASE_URL}/imoveis/", json=payload)
                            
                            if response.status_code == 200:
                                st.success(f"✅ Imóvel {mode.lower()} com sucesso!")
                                st.balloons()
                                if 'selected_ad' in st.session_state:
                                    del st.session_state.selected_ad
                                st.rerun()
                            else:
                                st.error(f"❌ Erro ao {mode.lower()}: {response.text}")
                        except Exception as e:
                            st.error(f"🔌 Erro de conexão com a API: {str(e)}")

            ad_form()
        
        with tab2:
            st.subheader("Lista de Todos os Imóveis")
            
            if st.button("🔄 Atualizar Lista"):
                st.rerun()
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/imoveis/")
                if response.status_code == 200:
                    imoveis = response.json()
                    
                    if imoveis:
                        st.write(f"**Total de imóveis:** {len(imoveis)}")
                        
                        for i, imovel in enumerate(imoveis):
                            with st.expander(f"🏠 {imovel.get('titulo', 'Sem título')} (ID: {imovel.get('id', 'N/A')})"):
                                st.write(f"**Descrição:** {imovel.get('descricao', '')}")
                                st.write(f"**Especificações:** {', '.join(imovel.get('especificacoes', []))}")
                    else:
                        st.info("📭 Nenhum imóvel cadastrado ainda.")
                else:
                    st.error("❌ Erro ao carregar imóveis")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
        
        with tab3:
            st.subheader("Editar Imóvel")
            
            search_method = st.radio("Buscar por:", ["ID", "Título"])
            
            if search_method == "ID":
                search_value = st.text_input("Digite o ID do imóvel:")
            else:
                search_value = st.text_input("Digite o título do imóvel:")
            
            if st.button("🔍 Buscar Imóvel") and search_value:
                try:
                    response = requests.get(f"{FASTAPI_BASE_URL}/imoveis/")
                    if response.status_code == 200:
                        imoveis = response.json()
                        
                        found_imovel = None
                        if search_method == "ID":
                            found_imovel = next((i for i in imoveis if i.get('id') == search_value), None)
                        else:
                            found_imovel = next((i for i in imoveis if search_value.lower() in i.get('titulo', '').lower()), None)
                        
                        if found_imovel:
                            st.session_state.edit_imovel = found_imovel
                            st.success("✅ Imóvel encontrado!")
                        else:
                            st.error("❌ Imóvel não encontrado")
                except Exception as e:
                    st.error(f"🔌 Erro de conexão com a API: {str(e)}")
            
            # Formulário de edição
            if 'edit_imovel' in st.session_state:
                imovel = st.session_state.edit_imovel
                st.write("---")
                st.write("**Editando imóvel:**")
                
                with st.form("edit_form"):
                    new_titulo = st.text_input("Título", value=imovel.get('titulo', ''))
                    new_descricao = st.text_area("Descrição", value=imovel.get('descricao', ''))
                    new_specs = st.text_area(
                        "Especificações (separadas por vírgula)", 
                        value=', '.join(imovel.get('especificacoes', []))
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Salvar Alterações"):
                            if new_titulo and new_descricao and new_specs:
                                especificacoes = [s.strip() for s in new_specs.split(",") if s.strip()]
                                update_data = {
                                    "titulo": new_titulo,
                                    "descricao": new_descricao,
                                    "especificacoes": especificacoes
                                }
                                
                                try:
                                    response = requests.put(
                                        f"{FASTAPI_BASE_URL}/imoveis/{imovel['id']}", 
                                        json=update_data
                                    )
                                    if response.status_code == 200:
                                        st.success("✅ Imóvel atualizado com sucesso!")
                                        del st.session_state.edit_imovel
                                        time.sleep(0.5) 
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erro ao atualizar: {response.text}")
                                except Exception as e:
                                    st.error("🔌 Erro de conexão com a API")
                            else:
                                st.warning("⚠️ Preencha todos os campos!")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancelar"):
                            del st.session_state.edit_imovel
                            st.rerun()
        
        with tab4:
            st.subheader("Excluir Imóvel")
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/imoveis/")
                if response.status_code == 200:
                    imoveis = response.json()
                    
                    if imoveis:
                        st.warning("⚠️ **ATENÇÃO:** Esta ação não pode ser desfeita!")
                        
                        for imovel in imoveis:
                            with st.container():
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.write(f"**{imovel.get('titulo', 'Sem título')}**")
                                    st.write(f"ID: {imovel.get('id', 'N/A')}")
                                
                                with col2:
                                    imovel_id = imovel.get('id', f'unknown_{hash(str(imovel))}')
                                    if st.button("🗑️ Excluir", key=f"delete_{imovel_id}", type="secondary"):
                                        st.session_state[f"confirm_delete_{imovel_id}"] = True
                                
                                if st.session_state.get(f"confirm_delete_{imovel_id}", False):
                                    st.error(f"Tem certeza que deseja excluir: **{imovel.get('titulo', 'Sem título')}**?")
                                    col_yes, col_no = st.columns(2)
                                    
                                    with col_yes:
                                        if st.button("✅ Sim, excluir", key=f"yes_{imovel_id}"):
                                            try:
                                                delete_response = requests.delete(f"{FASTAPI_BASE_URL}/imoveis/{imovel['id']}")
                                                if delete_response.status_code == 200:
                                                    st.success("✅ Imóvel excluído com sucesso!")
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Erro ao excluir imóvel")
                                            except Exception as e:
                                                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                                    
                                    with col_no:
                                        if st.button("❌ Cancelar", key=f"no_{imovel_id}"):
                                            del st.session_state[f"confirm_delete_{imovel_id}"]
                                            st.rerun()
                                
                                st.divider()
                    else:
                        st.info("📭 Nenhum imóvel para excluir.")
                else:
                    st.error("❌ Erro ao carregar imóveis")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
    
    elif page == "🕷️ Crawler":
        st.header("🕷️ Crawler de Imóveis")
        st.write("Use esta ferramenta para buscar e importar imóveis do ChavesNaMao.com.br")
        
        with st.form("crawler_config"):
            st.subheader("Configurações de Busca")
            
            col1, col2 = st.columns(2)
            
            with col1:
                type_listing = st.selectbox(
                    "Tipo de Listagem",
                    ["venda", "aluguel"],
                    index=0
                )
                
                state = st.text_input("Estado (sigla)", value="go", max_chars=2)
                city = st.text_input("Cidade", value="goiania")
                
            with col2:
                max_results = st.number_input(
                    "Número máximo de imóveis", 
                    min_value=5, 
                    max_value=100, 
                    value=20,
                    step=5,
                    help="Quantos imóveis buscar (máximo 100)"
                )
            
            
            crawl_button = st.form_submit_button("🚀 Iniciar Crawler", type="primary", use_container_width=True)
        
        if crawl_button:
            st.info("🔄 Iniciando processo de crawling...")
            
            search_params = {
                "transaction_type": type_listing,
                "state": state.lower(),
                "city": city.lower(),
                "max_results": max_results
            }
            
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    import sys
                    import os
                    import asyncio
                    import json
                    
                    crawler_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawler')
                    if crawler_path not in sys.path:
                        sys.path.insert(0, crawler_path)
                    
                    from crawler_chavesnamao import search_properties
                    
                    status_text.text(f"📍 Buscando em ChavesNaMao: {city}/{state} - {type_listing}")
                    
                    status_text.text("🕷️ Executando crawler...")
                    progress_bar.progress(25)
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    listings = loop.run_until_complete(search_properties(search_params))
                    loop.close()
                    
                    if not listings:
                        st.error("❌ Nenhum imóvel encontrado com os critérios especificados.")
                        return
                    
                    status_text.text(f"✅ {len(listings)} imóveis encontrados!")
                    progress_bar.progress(50)
                    
                    status_text.text("📤 Inserindo imóveis no sistema...")
                    
                    success_count = 0
                    error_count = 0
                    
                    for i, listing in enumerate(listings):
                        try:
                            especificacoes = []
                            
                            if listing.get('price_text'):
                                especificacoes.append(listing['price_text'])
                            elif listing.get('price'):
                                especificacoes.append(f"R$ {listing['price']:,.2f}")
                            
                            if listing.get('area'):
                                especificacoes.append(f"{listing['area']}m²")
                            
                            if listing.get('bedrooms'):
                                especificacoes.append(f"{listing['bedrooms']} quartos")
                            
                            if listing.get('bathrooms'):
                                especificacoes.append(f"{listing['bathrooms']} banheiros")
                            
                            if listing.get('parking_spaces'):
                                especificacoes.append(f"{listing['parking_spaces']} vagas")
                            
                            if listing.get('property_type'):
                                especificacoes.append(listing['property_type'])
                            
                            if listing.get('features'):
                                especificacoes.extend(listing['features'][:5])  # Limitar a 5 características
                            
                            titulo = listing.get('title') or f"{listing.get('property_type', 'Imóvel')} - {listing.get('neighborhood', 'Sem bairro')}"
                            
                            descricao_parts = []
                            if listing.get('description'):
                                descricao_parts.append(listing['description'])
                            
                            if listing.get('address'):
                                descricao_parts.append(f"Endereço: {listing['address']}")
                            
                            if listing.get('neighborhood'):
                                descricao_parts.append(f"Bairro: {listing['neighborhood']}")
                                
                            if listing.get('city') and listing.get('state'):
                                descricao_parts.append(f"Cidade: {listing['city']}/{listing['state']}")
                            
                            if listing.get('advertiser'):
                                descricao_parts.append(f"Anunciante: {listing['advertiser']}")
                            
                            if listing.get('url'):
                                descricao_parts.append(f"Link: {listing['url']}")
                            
                            descricao = " | ".join(descricao_parts) if descricao_parts else "Sem descrição disponível"
                            
                            payload = {
                                "titulo": titulo[:200],  # Limitar tamanho
                                "descricao": descricao[:1000],  # Limitar tamanho
                                "especificacoes": especificacoes
                            }
                            
                            response = requests.post(f"{FASTAPI_BASE_URL}/imoveis/", json=payload)
                            
                            if response.status_code == 200:
                                success_count += 1
                            else:
                                error_count += 1
                                st.warning(f"⚠️ Erro ao inserir: {titulo[:50]}...")
                            
                            progress = 50 + int((i + 1) / len(listings) * 50)
                            progress_bar.progress(progress)
                            status_text.text(f"📤 Processando {i+1}/{len(listings)} imóveis...")
                            
                        except Exception as e:
                            error_count += 1
                            st.warning(f"⚠️ Erro ao processar imóvel: {str(e)}")
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ Processo concluído! {success_count} imóveis inseridos com sucesso.")
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} imóveis não puderam ser inseridos.")
                    
                    if success_count > 0:
                        with st.expander("📋 Ver imóveis processados"):
                            for listing in listings[:5]:  # Mostrar apenas 5 primeiros
                                st.write(f"**{listing.get('title', 'Sem título')}**")
                                if listing.get('address'):
                                    st.write(f"📍 {listing['address']}")
                                if listing.get('neighborhood'):
                                    st.write(f"🏘️ {listing['neighborhood']}")
                                if listing.get('price_text'):
                                    st.write(f"💰 {listing['price_text']}")
                                elif listing.get('price'):
                                    st.write(f"💰 R$ {listing['price']:,.2f}")
                                if listing.get('area'):
                                    st.write(f"📐 {listing['area']}m²")
                                st.divider()
                    
                except ImportError as e:
                    st.error(f"❌ Erro ao importar o crawler: {str(e)}")
                    st.info("💡 Certifique-se de que o arquivo crawler.py está na pasta crawler/")
                except Exception as e:
                    st.error(f"❌ Erro durante o processo: {str(e)}")
                    st.info("💡 Verifique os logs para mais detalhes")
    
    elif page == "👔 Corretores":
        st.header("👔 Gestão de Corretores")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
        
        with tab1:
            st.subheader("Lista de Corretores")
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/corretores/")
                if response.status_code == 200:
                    corretores = response.json()
                    
                    if corretores:
                        for corretor in corretores:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.write(f"**{corretor.get('nome', 'Sem nome')}**")
                                    st.write(f"📧 {corretor.get('email', 'N/A')}")
                                    st.write(f"📱 {corretor.get('telefone', 'N/A')}")
                                    st.write(f"🏆 CRECI: {corretor.get('creci', 'N/A')}")
                                    
                                    if corretor.get('especialidades'):
                                        st.write(f"🎯 Especialidades: {', '.join(corretor['especialidades'])}")
                                    
                                    status = "✅ Ativo" if corretor.get('ativo', True) else "❌ Inativo"
                                    st.write(f"Status: {status}")
                                
                                with col2:
                                    st.write(f"**ID:** {corretor.get('id', 'N/A')}")
                                
                                st.divider()
                    else:
                        st.info("📭 Nenhum corretor cadastrado.")
                else:
                    st.error("❌ Erro ao carregar corretores")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
        
        with tab2:
            st.subheader("Adicionar Novo Corretor")
            
            with st.form("add_corretor"):
                nome = st.text_input("Nome completo *")
                email = st.text_input("Email *")
                telefone = st.text_input("Telefone *")
                creci = st.text_input("CRECI *")
                ativo = st.checkbox("Ativo", value=True)
                
                especialidades = st.multiselect(
                    "Especialidades",
                    ["Residencial", "Comercial", "Rural", "Industrial", "Lançamentos", "Temporada"]
                )
                
                cidades_disponiveis = []
                try:
                    response = requests.get(f"{FASTAPI_BASE_URL}/cidades/")
                    if response.status_code == 200:
                        cidades = response.json()
                        cidades_disponiveis = [(c['id'], f"{c['nome']} - {c['estado']}") for c in cidades]
                except:
                    pass
                
                cidades_atendidas = st.multiselect(
                    "Cidades atendidas",
                    options=[c[0] for c in cidades_disponiveis],
                    format_func=lambda x: next((c[1] for c in cidades_disponiveis if c[0] == x), x)
                )
                
                if st.form_submit_button("➕ Adicionar Corretor"):
                    if nome and email and telefone and creci:
                        corretor_data = {
                            "nome": nome,
                            "email": email,
                            "telefone": telefone,
                            "creci": creci,
                            "ativo": ativo,
                            "especialidades": especialidades,
                            "cidades_atendidas": cidades_atendidas
                        }
                        
                        try:
                            response = requests.post(f"{FASTAPI_BASE_URL}/corretores/", json=corretor_data)
                            if response.status_code == 200:
                                st.success("✅ Corretor adicionado com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"❌ Erro ao adicionar: {response.text}")
                        except Exception as e:
                            st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                    else:
                        st.error("⚠️ Preencha todos os campos obrigatórios!")
        
        with tab3:
            st.subheader("Editar Corretor")
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/corretores/")
                if response.status_code == 200:
                    corretores = response.json()
                    
                    if corretores:
                        corretor_selecionado = st.selectbox(
                            "Selecione um corretor para editar",
                            options=corretores,
                            format_func=lambda x: f"{x['nome']} - CRECI: {x['creci']}"
                        )
                        
                        if corretor_selecionado:
                            with st.form("edit_corretor"):
                                nome = st.text_input("Nome completo *", value=corretor_selecionado['nome'])
                                email = st.text_input("Email *", value=corretor_selecionado['email'])
                                telefone = st.text_input("Telefone *", value=corretor_selecionado['telefone'])
                                creci = st.text_input("CRECI *", value=corretor_selecionado['creci'])
                                ativo = st.checkbox("Ativo", value=corretor_selecionado.get('ativo', True))
                                
                                especialidades = st.multiselect(
                                    "Especialidades",
                                    ["Residencial", "Comercial", "Rural", "Industrial", "Lançamentos", "Temporada"],
                                    default=corretor_selecionado.get('especialidades', [])
                                )
                                
                                cidades_disponiveis = []
                                try:
                                    cidades_response = requests.get(f"{FASTAPI_BASE_URL}/cidades/")
                                    if cidades_response.status_code == 200:
                                        cidades = cidades_response.json()
                                        cidades_disponiveis = [(c['id'], f"{c['nome']} - {c['estado']}") for c in cidades]
                                except:
                                    pass
                                
                                cidades_atendidas = st.multiselect(
                                    "Cidades atendidas",
                                    options=[c[0] for c in cidades_disponiveis],
                                    format_func=lambda x: next((c[1] for c in cidades_disponiveis if c[0] == x), x),
                                    default=corretor_selecionado.get('cidades_atendidas', [])
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                                        if nome and email and telefone and creci:
                                            corretor_data = {
                                                "nome": nome,
                                                "email": email,
                                                "telefone": telefone,
                                                "creci": creci,
                                                "ativo": ativo,
                                                "especialidades": especialidades,
                                                "cidades_atendidas": cidades_atendidas
                                            }
                                            
                                            try:
                                                update_response = requests.put(
                                                    f"{FASTAPI_BASE_URL}/corretores/{corretor_selecionado['id']}", 
                                                    json=corretor_data
                                                )
                                                if update_response.status_code == 200:
                                                    st.success("✅ Corretor atualizado com sucesso!")
                                                    time.sleep(1)
                                                    st.rerun()
                                                else:
                                                    st.error(f"❌ Erro ao atualizar: {update_response.text}")
                                            except Exception as e:
                                                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                                        else:
                                            st.error("⚠️ Preencha todos os campos obrigatórios!")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.rerun()
                    else:
                        st.info("📭 Nenhum corretor cadastrado para editar.")
                else:
                    st.error("❌ Erro ao carregar corretores")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
        
        with tab4:
            st.subheader("Excluir Corretor")
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/corretores/")
                if response.status_code == 200:
                    corretores = response.json()
                    
                    if corretores:
                        st.warning("⚠️ **ATENÇÃO:** Esta ação não pode ser desfeita!")
                        
                        for corretor in corretores:
                            with st.container():
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.write(f"**{corretor.get('nome', 'Sem nome')}**")
                                    st.write(f"📧 {corretor.get('email', 'N/A')} | 📱 {corretor.get('telefone', 'N/A')}")
                                    st.write(f"🏆 CRECI: {corretor.get('creci', 'N/A')}")
                                    status = "✅ Ativo" if corretor.get('ativo', True) else "❌ Inativo"
                                    st.write(f"Status: {status}")
                                
                                with col2:
                                    corretor_id = corretor.get('id', f'unknown_{hash(str(corretor))}')
                                    if st.button("🗑️ Excluir", key=f"delete_corretor_{corretor_id}", type="secondary"):
                                        st.session_state[f"confirm_delete_corretor_{corretor_id}"] = True
                                
                                if st.session_state.get(f"confirm_delete_corretor_{corretor_id}", False):
                                    st.error(f"Tem certeza que deseja excluir: **{corretor.get('nome', 'Sem nome')}**?")
                                    col_yes, col_no = st.columns(2)
                                    
                                    with col_yes:
                                        if st.button("✅ Sim, excluir", key=f"yes_corretor_{corretor_id}"):
                                            try:
                                                delete_response = requests.delete(f"{FASTAPI_BASE_URL}/corretores/{corretor['id']}")
                                                if delete_response.status_code == 200:
                                                    st.success("✅ Corretor excluído com sucesso!")
                                                    time.sleep(1)
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Erro ao excluir corretor")
                                            except Exception as e:
                                                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                                    
                                    with col_no:
                                        if st.button("❌ Cancelar", key=f"no_corretor_{corretor_id}"):
                                            del st.session_state[f"confirm_delete_corretor_{corretor_id}"]
                                            st.rerun()
                                
                                st.divider()
                    else:
                        st.info("📭 Nenhum corretor para excluir.")
                else:
                    st.error("❌ Erro ao carregar corretores")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
    
    elif page == "🏙️ Cidades":
        st.header("🏙️ Gestão de Cidades")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "➕ Adicionar", "✏️ Editar", "🗑️ Excluir"])
        
        with tab1:
            st.subheader("Lista de Cidades")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                estado_filtro = st.selectbox(
                    "Filtrar por estado",
                    ["Todos", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                     "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", 
                     "RO", "RR", "SC", "SP", "SE", "TO"]
                )
            
            try:
                if estado_filtro != "Todos":
                    response = requests.get(f"{FASTAPI_BASE_URL}/cidades/estado/{estado_filtro}")
                else:
                    response = requests.get(f"{FASTAPI_BASE_URL}/cidades/")
                
                if response.status_code == 200:
                    cidades = response.json()
                    
                    if cidades:
                        # Agrupar por estado
                        from collections import defaultdict
                        cidades_por_estado = defaultdict(list)
                        for cidade in cidades:
                            cidades_por_estado[cidade.get('estado', 'N/A')].append(cidade)
                        
                        for estado, cidades_estado in sorted(cidades_por_estado.items()):
                            st.write(f"### {estado}")
                            
                            for cidade in sorted(cidades_estado, key=lambda x: x.get('nome', '')):
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 2, 1])
                                    
                                    with col1:
                                        st.write(f"**{cidade.get('nome', 'Sem nome')}**")
                                        if cidade.get('regiao'):
                                            st.write(f"🗺️ Região: {cidade['regiao']}")
                                    
                                    with col2:
                                        if cidade.get('populacao'):
                                            st.write(f"👥 População: {cidade['populacao']:,}")
                                        if cidade.get('area_km2'):
                                            st.write(f"📏 Área: {cidade['area_km2']:,.2f} km²")
                                    
                                    with col3:
                                        st.write(f"ID: {cidade.get('id', 'N/A')[:8]}...")
                            
                            st.divider()
                    else:
                        st.info("📭 Nenhuma cidade cadastrada.")
                else:
                    st.error("❌ Erro ao carregar cidades")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
        
        with tab2:
            st.subheader("Adicionar Nova Cidade")
            
            with st.form("add_cidade"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome da cidade *")
                    estado = st.selectbox(
                        "Estado (UF) *",
                        ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                         "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", 
                         "RO", "RR", "SC", "SP", "SE", "TO"]
                    )
                    regiao = st.selectbox(
                        "Região",
                        ["", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
                    )
                
                with col2:
                    populacao = st.number_input("População", min_value=0, value=0)
                    area_km2 = st.number_input("Área (km²)", min_value=0.0, value=0.0)
                
                if st.form_submit_button("➕ Adicionar Cidade"):
                    if nome and estado:
                        cidade_data = {
                            "nome": nome,
                            "estado": estado
                        }
                        
                        if regiao:
                            cidade_data["regiao"] = regiao
                        if populacao > 0:
                            cidade_data["populacao"] = populacao
                        if area_km2 > 0:
                            cidade_data["area_km2"] = area_km2
                        
                        try:
                            response = requests.post(f"{FASTAPI_BASE_URL}/cidades/", json=cidade_data)
                            if response.status_code == 200:
                                st.success("✅ Cidade adicionada com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"❌ Erro ao adicionar: {response.text}")
                        except Exception as e:
                            st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                    else:
                        st.error("⚠️ Preencha todos os campos obrigatórios!")
        
        with tab3:
            st.subheader("Editar Cidade")
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/cidades/")
                if response.status_code == 200:
                    cidades = response.json()
                    
                    if cidades:
                        cidades_por_estado = {}
                        for cidade in cidades:
                            estado = cidade.get('estado', 'N/A')
                            if estado not in cidades_por_estado:
                                cidades_por_estado[estado] = []
                            cidades_por_estado[estado].append(cidade)
                        
                        estado_selecionado = st.selectbox(
                            "Selecione o estado",
                            options=sorted(cidades_por_estado.keys())
                        )
                        
                        if estado_selecionado:
                            cidade_selecionada = st.selectbox(
                                "Selecione a cidade para editar",
                                options=cidades_por_estado[estado_selecionado],
                                format_func=lambda x: x['nome']
                            )
                            
                            if cidade_selecionada:
                                with st.form("edit_cidade"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        nome = st.text_input("Nome da cidade *", value=cidade_selecionada['nome'])
                                        estado = st.selectbox(
                                            "Estado (UF) *",
                                            ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                                             "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", 
                                             "RO", "RR", "SC", "SP", "SE", "TO"],
                                            index=["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                                                   "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", 
                                                   "RO", "RR", "SC", "SP", "SE", "TO"].index(cidade_selecionada['estado'])
                                        )
                                        regiao = st.selectbox(
                                            "Região",
                                            ["", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
                                            index=["", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"].index(
                                                cidade_selecionada.get('regiao', '')
                                            ) if cidade_selecionada.get('regiao') else 0
                                        )
                                    
                                    with col2:
                                        populacao = st.number_input(
                                            "População", 
                                            min_value=0, 
                                            value=cidade_selecionada.get('populacao', 0)
                                        )
                                        area_km2 = st.number_input(
                                            "Área (km²)", 
                                            min_value=0.0, 
                                            value=float(cidade_selecionada.get('area_km2', 0.0))
                                        )
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                                            if nome and estado:
                                                cidade_data = {
                                                    "nome": nome,
                                                    "estado": estado
                                                }
                                                
                                                if regiao:
                                                    cidade_data["regiao"] = regiao
                                                if populacao > 0:
                                                    cidade_data["populacao"] = populacao
                                                if area_km2 > 0:
                                                    cidade_data["area_km2"] = area_km2
                                                
                                                try:
                                                    update_response = requests.put(
                                                        f"{FASTAPI_BASE_URL}/cidades/{cidade_selecionada['id']}", 
                                                        json=cidade_data
                                                    )
                                                    if update_response.status_code == 200:
                                                        st.success("✅ Cidade atualizada com sucesso!")
                                                        time.sleep(1)
                                                        st.rerun()
                                                    else:
                                                        st.error(f"❌ Erro ao atualizar: {update_response.text}")
                                                except Exception as e:
                                                    st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                                            else:
                                                st.error("⚠️ Preencha todos os campos obrigatórios!")
                                    
                                    with col2:
                                        if st.form_submit_button("❌ Cancelar"):
                                            st.rerun()
                    else:
                        st.info("📭 Nenhuma cidade cadastrada para editar.")
                else:
                    st.error("❌ Erro ao carregar cidades")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")
        
        with tab4:
            st.subheader("Excluir Cidade")
            
            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/cidades/")
                if response.status_code == 200:
                    cidades = response.json()
                    
                    if cidades:
                        st.warning("⚠️ **ATENÇÃO:** Esta ação não pode ser desfeita!")
                        
                        for cidade in cidades:
                            with st.container():
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.write(f"**{cidade.get('nome', 'Sem nome')} - {cidade.get('estado', 'N/A')}**")
                                    st.write(f"ID: {cidade.get('id', 'N/A')}")
                                
                                with col2:
                                    cidade_id = cidade.get('id', f'unknown_{hash(str(cidade))}')
                                    if st.button("🗑️ Excluir", key=f"delete_cidade_{cidade_id}", type="secondary"):
                                        try:
                                            delete_response = requests.delete(f"{FASTAPI_BASE_URL}/cidades/{cidade['id']}")
                                            if delete_response.status_code == 200:
                                                st.success("✅ Cidade excluída com sucesso!")
                                                st.rerun()
                                            else:
                                                st.error("❌ Erro ao excluir cidade")
                                        except Exception as e:
                                            st.error(f"🔌 Erro de conexão com a API: {str(e)}")
                                
                                st.divider()
                    else:
                        st.info("📭 Nenhuma cidade para excluir.")
                else:
                    st.error("❌ Erro ao carregar cidades")
            except Exception as e:
                st.error(f"🔌 Erro de conexão com a API: {str(e)}")

if __name__ == "__main__":
    main()