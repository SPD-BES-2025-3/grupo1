import random
import requests
import streamlit as st

# Configuração da página e tema escuro
st.set_page_config(page_title="Sistema de Cadastro", page_icon="🏠")

# CSS para tema escuro
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background-color: #1F1F1F; color: white; }
    [data-testid="stSidebar"] .stButton>button { background-color: #333; color: white; width: 100%; height: 40px; border-radius: 5px; margin-bottom: 5px; border: none; }
    [data-testid="stSidebar"] .stButton>button:hover { background-color: #444; }
    [data-testid="stSidebar"] .active { background-color: #555; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-weight: bold; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True
)

def fetch_ads():
    response = requests.get("http://localhost:8181/articles/")

    if response.status_code == 200:
        data = response.json()  # Se a resposta for JSON
        st.session_state.ads = data
        print(data)
    else:
        st.session_state.ads = []
        print(f"Erro: {response.status_code}")

def fetch_cities():
    response = requests.get("http://localhost:8181/cities/")

    if response.status_code == 200:
        data = response.json()  # Se a resposta for JSON
        st.session_state.cidades = data
        # print(data)
    else:
        st.session_state.ads = []
        print(f"Erro: {response.status_code}")

def fetch_annunciantes():
    response = requests.get("http://localhost:8181/announcers/")  # ou "/anunciantes/" conforme sua API
    if response.status_code == 200:
        st.session_state.anunciantes = response.json()
        # DEBUG: imprima pra checar o formato que vem do servidor
        st.write("Anunciantes do servidor:", st.session_state.anunciantes)
    else:
        st.session_state.anunciantes = []
        print(f"Erro ao buscar anunciantes: {response.status_code}")


def delete_ad(idx):
    ad = st.session_state.ads[idx]
    print(ad)
    id = ad["_id"]

    response = requests.delete(f"http://localhost:8181/articles/{id}")

    if response.status_code == 200:
        fetch_ads()
    else:
        print(f"Erro: {response.status_code}")

fetch_ads()
fetch_cities()
fetch_annunciantes()

# Estado inicial com registros de exemplo
if "ads" not in st.session_state:
    st.session_state.ads = [
        {
            "titulo": "Apartamento Centro",
            "descricao": "Apartamento de 2 quartos no centro da cidade.",
            "preco": 350000.0,
            "area": 85.0,
            "quartos": 2,
            "banheiros": 2,
            "suites": 1,
            "caracteristicas": ["Varanda", "Elevador", "Garagem"],
            "cidade": "São Paulo",
            "anunciante": "Imobiliária Exemplo"
        }
    ]
if "cidades" not in st.session_state:
    st.session_state.cidades = [
        {"nome": "São Paulo", "estado": "SP"}
    ]
if "anunciantes" not in st.session_state:
    st.session_state.anunciantes = [
        {"nome": "Imobiliária Exemplo", "telefone": "(11) 1234-5678"}
    ]
if "page" not in st.session_state: st.session_state.page = "App"
if "subpage" not in st.session_state: st.session_state.subpage = "Buscar"
for obj in ("ad", "city", "ann"):
    key = f"selected_{obj}"
    if key not in st.session_state:
        st.session_state[key] = None

# Navegação principal
st.sidebar.title("🗂️ Sistema de Cadastro")
main_menu = ["App", "Anúncios", "Cidades", "Anunciantes"]
icons = {"App": "🤖", "Anúncios": "🏠", "Cidades": "🌆", "Anunciantes": "📞"}
for item in main_menu:
    if st.session_state.page == item:
        st.sidebar.markdown(f"<div class='active'>{icons[item]} {item}</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button(f"{icons[item]} {item}", key=item):
            st.session_state.page = item
            st.session_state.subpage = "Buscar"
            st.session_state.selected_ad = None
            st.session_state.selected_city = None
            st.session_state.selected_ann = None

# CRUD Anúncios
def ad_form():
    mode = "Editar" if st.session_state.selected_ad is not None else "Criar"

    # Começa o formulário
    with st.form(key="ad_form"):
        st.subheader(f"{mode} Anúncio")

        # Carrega valores iniciais para edição
        initial = {}
        if st.session_state.selected_ad is not None:
            initial = st.session_state.ads[st.session_state.selected_ad]

        # Campos básicos
        titulo = st.text_input("Título", value=initial.get('title', ''))
        descricao = st.text_area("Descrição", value=initial.get('description', ''))
        preco = st.number_input(
            "Preço (R$)", min_value=0.0, step=50.0,
            value=initial.get('price', 0.0)
        )
        area = st.number_input(
            "Área (m²)", min_value=0.0, step=1.0,
            value=initial.get('area', 0.0)
        )
        quartos = st.number_input(
            "Quartos", min_value=0, step=1,
            value=initial.get('bed_rooms', 0)
        )
        banheiros = st.number_input(
            "Banheiros", min_value=0, step=1,
            value=initial.get('bath_rooms', 0)
        )
        suites = st.number_input(
            "Suítes", min_value=0, step=1,
            value=initial.get('suites', 0)
        )
        caracteristicas = st.text_input(
            "Características (separadas por vírgula)",
            value=", ".join(initial.get('features', []))
        )

        # Listas de opções
        city_names = [c['name'] for c in st.session_state.cidades]
        ann_names  = [a['name'] for a in st.session_state.anunciantes]

        # Valores padrão para edição
        default_city = ""
        default_ann  = ""
        if st.session_state.selected_ad is not None:
            ad = st.session_state.ads[st.session_state.selected_ad]
            default_city = ad.get('city', {}).get('name', '')
            default_ann  = ad.get('announcer', {}).get('name', '')

        # Constrói opções e índices
        city_opts = [""] + city_names
        ann_opts  = [""] + ann_names
        city_index = city_opts.index(default_city) if default_city in city_opts else 0
        ann_index  = ann_opts.index(default_ann)  if default_ann in ann_opts  else 0

        # Selectboxes com valor pré-selecionado
        cidade_sel = st.selectbox("Cidade", options=city_opts, index=city_index)
        ann_sel    = st.selectbox("Anunciante", options=ann_opts, index=ann_index)

        # Botão de envio
        if st.form_submit_button(mode):
            # Monta payload
            payload = {
                "title": titulo,
                "description": descricao,
                "price": preco,
                "area": area,
                "bed_rooms": quartos,
                "bath_rooms": banheiros,
                "suites": suites,
                "features": [c.strip() for c in caracteristicas.split(",") if c.strip()],
                "city_id": next((c['_id'] for c in st.session_state.cidades if c['name'] == cidade_sel), None),
                "announcer_id": next((a['_id'] for a in st.session_state.anunciantes if a['name'] == ann_sel), None),
            }
            # Envia POST ou PUT conforme o modo
            if st.session_state.selected_ad is None:
                requests.post("http://localhost:8181/articles/", json=payload)
            else:
                art_id = st.session_state.ads[st.session_state.selected_ad]["_id"]
                requests.put(f"http://localhost:8181/articles/{art_id}", json=payload)

            # Atualiza lista e feedback
            fetch_ads()
            st.success(f"Anúncio {mode.lower()} com sucesso!")
            st.session_state.selected_ad = None





def show_ads_list():
    st.subheader("Anúncios")
    if not st.session_state.ads:
        st.info("Nenhum anúncio cadastrado.")
        return
    for idx, ad in enumerate(st.session_state.ads):
        cols = st.columns([4,1,1])
        cols[0].markdown(f"**{ad['title']}** ({ad['city']['name']}) - anunciante | R$ {ad['price']}")
        if cols[1].button("Editar", key=f"edit_ad_{idx}"):
            st.session_state.selected_ad = idx
            st.session_state.subpage = "Adicionar"   # <<< aqui!
            # st.experimental_rerun()
            st.stop()
        if cols[2].button("Excluir", key=f"del_ad_{idx}"):
            delete_ad(idx)
            st.success("Anúncio excluído")

# CRUD Cidades
def city_form():
    mode = "Editar" if st.session_state.selected_city is not None else "Criar"
    with st.form(key="city_form"):
        st.subheader(f"{mode} Cidade")
        nome = st.text_input(
            "Nome",
            value=(
                st.session_state.cidades[st.session_state.selected_city]["name"]
                if st.session_state.selected_city is not None
                else ""
            ),
        )
        estado = st.text_input(
            "Estado",
            value=(
                st.session_state.cidades[st.session_state.selected_city]["state"]
                if st.session_state.selected_city is not None
                else ""
            ),
        )

        if st.form_submit_button(mode):
            # Monta o payload com os campos exatos do Pydantic City
            payload = {
                "name": nome,
                "state": estado
            }

            # DEBUG: veja o JSON antes de enviar
            st.write("Payload de cidade:", payload)

            # Escolhe POST ou PUT conforme o modo
            if st.session_state.selected_city is None:
                response = requests.post(
                    "http://localhost:8181/cities/", json=payload
                )
            else:
                existing_id = st.session_state.cidades[st.session_state.selected_city]["_id"]
                response = requests.put(
                    f"http://localhost:8181/cities/{existing_id}",
                    json=payload
                )

            # Mostra status e corpo pra ajudar no debug
            st.write("Status:", response.status_code, "Resposta:", response.text)

            if response.ok:
                st.success(f"Cidade {mode.lower()}ada com sucesso no servidor!")
                fetch_cities()  # recarrega a lista do backend
            else:
                st.error(f"Erro ao {mode.lower()} cidade: {response.status_code}")

            # Reseta a seleção pra voltar à lista
            st.session_state.selected_city = None

def show_cities_list():
    st.subheader("Cidades")
    if not st.session_state.cidades:
        st.info("Nenhuma cidade cadastrada.")
        return
    for idx, city in enumerate(st.session_state.cidades):
        cols = st.columns([4,1,1])
        cols[0].markdown(f"**{city['name']}** - {city['state']}")
        if cols[1].button("Editar", key=f"edit_city_{idx}"):
            st.session_state.selected_city = idx
            st.session_state.subpage = "Adicionar"   # <<< aqui!
            st.stop()
        # if cols[2].button("Excluir", key=f"del_city_{idx}"):
        #     st.session_state.cidades.pop(idx)
        #     st.success("Cidade excluída")

# CRUD Anunciantes
def ann_form():
    mode = "Editar" if st.session_state.selected_ann is not None else "Criar"
    with st.form(key="ann_form"):
        st.subheader(f"{mode} Anunciante")
        nome = st.text_input("Nome", value=(st.session_state.anunciantes[st.session_state.selected_ann]['nome'] if st.session_state.selected_ann is not None else ""))
        telefone = st.text_input("Telefone", value=(st.session_state.anunciantes[st.session_state.selected_ann]['telefone'] if st.session_state.selected_ann is not None else ""))
        if st.form_submit_button(mode):
            ann = {"nome": nome, "telefone": telefone}
            if st.session_state.selected_ann is None:
                st.session_state.anunciantes.append(ann)
                st.success("Anunciante criado!")
            else:
                st.session_state.anunciantes[st.session_state.selected_ann] = ann
                st.success("Anunciante atualizado!")
            st.session_state.selected_ann = None

def show_ann_list():
    st.subheader("Anunciantes")
    if not st.session_state.anunciantes:
        st.info("Nenhum anunciante cadastrado.")
        return
    for idx, ann in enumerate(st.session_state.anunciantes):
        cols = st.columns([4,1,1])
        cols[0].markdown(f"**{ann['nome']}** - {ann['telefone']}")
        if cols[1].button("Editar", key=f"edit_ann_{idx}"):
            st.session_state.selected_ann = idx
            st.session_state.subpage = "Adicionar"   # <<< aqui!
            st.stop()
        # if cols[2].button("Excluir", key=f"del_ann_{idx}"):
        #     st.session_state.anunciantes.pop(idx)
        #     st.success("Anunciante excluído")


def get_llm_response(prompt: str, n_results: int = 5):
    try:
        resp = requests.get(
            "http://localhost:8181/search",
            params={"query": prompt, "n_results": n_results},
            timeout=5
        )
        resp.raise_for_status()
        results = resp.json()

        # Exibe cada resultado como uma mensagem do assistente
        for idx, result in enumerate(results):
            with st.chat_message("assistant"):
                st.markdown(f"**Resultado {idx + 1}:**")
                for key, value in result.items():
                    st.markdown(f"- **{key}**: {value}")

                # Botões de feedback
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("👍", key=f"thumbs_up_{idx}"):
                        st.toast(f"Você marcou o Resultado {idx + 1} como relevante.")
                        # Aqui você pode adicionar a lógica para lidar com o feedback positivo
                with col2:
                    if st.button("👎", key=f"thumbs_down_{idx}"):
                        st.toast(f"Você marcou o Resultado {idx + 1} como irrelevante.")
                        # Aqui você pode adicionar a lógica para lidar com o feedback negativo

    except requests.RequestException as e:
        st.error(f"Erro na requisição ao /search: {e}")


# Roteamento de páginas
if st.session_state.page == "App":
    st.title("Dakila IA")

    # Inicializa o histórico e resultados
    if "messages" not in st.session_state:
        st.session_state.messages = [ {"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"} ]
    if "results" not in st.session_state:
        st.session_state.results = []         # lista de dicts retornados pela API
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}        # mapeia idx -> True/False

    # Exibe todo o histórico (mensagens de usuário + bot)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Caixa de input do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # armazena e exibe a mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # busca na API e guarda os resultados
        try:
            resp = requests.get(
                "http://localhost:8181/search",
                params={"query": prompt, "n_results": 5},
                timeout=5
            )
            resp.raise_for_status()
            st.session_state.results = resp.json()
        except:
            st.error("Erro ao chamar /search")
            st.session_state.results = []

    # **Agora** exibe cada resultado como mensagem do bot, com botões de feedback
    for idx, anuncio in enumerate(st.session_state.results):
        with st.chat_message("assistant"):
            st.markdown(f"**Resultado {idx+1}:**")
            for campo, valor in anuncio.items():
                st.markdown(f"- **{campo}**: {valor}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = True
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = False

        # Mostra feedback
        if idx in st.session_state.feedback:
            marcador = "Relevante 👍" if st.session_state.feedback[idx] else "Irrelevante 👎"
            st.markdown(f"> **Você marcou este anúncio como:** {marcador}")



else:
    # Submenu para CRUD
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Opções de {st.session_state.page}**")
    if st.sidebar.button("🔍 Buscar", key=f"{st.session_state.page}_buscar"):
        st.session_state.subpage = "Buscar"
    if st.sidebar.button("➕ Adicionar Registro", key=f"{st.session_state.page}_add"):
        st.session_state.subpage = "Adicionar"

    if st.session_state.page == "Anúncios":
        if st.session_state.subpage == "Buscar":
            show_ads_list()
        else:
            ad_form()
    elif st.session_state.page == "Cidades":
        if st.session_state.subpage == "Buscar":
            show_cities_list()
        else:
            city_form()
    elif st.session_state.page == "Anunciantes":
        if st.session_state.subpage == "Buscar":
            show_ann_list()
        else:
            ann_form()

# Função de chat
def get_llm_response(prompt: str) -> str:
    return random.choice([
        f"Resposta simulada: {prompt}",
        "Processando sua solicitação..."
    ])
