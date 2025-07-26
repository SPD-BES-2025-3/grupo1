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
    with st.form(key="ad_form"):
        st.subheader(f"{mode} Anúncio")
        titulo = st.text_input("Título", value=(st.session_state.ads[st.session_state.selected_ad]['title'] if st.session_state.selected_ad is not None else ""))
        descricao = st.text_area("Descrição", value=(st.session_state.ads[st.session_state.selected_ad]['description'] if st.session_state.selected_ad is not None else ""))
        preco = st.number_input("Preço (R$)", min_value=0.0, step=50.0, value=(st.session_state.ads[st.session_state.selected_ad]['price'] if st.session_state.selected_ad is not None else 0.0))
        area = st.number_input("Área (m²)", min_value=0.0, step=1.0, value=(st.session_state.ads[st.session_state.selected_ad]['area'] if st.session_state.selected_ad is not None else 0.0))
        quartos = st.number_input("Quartos", min_value=0, step=1, value=(st.session_state.ads[st.session_state.selected_ad]['bed_rooms'] if st.session_state.selected_ad is not None else 0))
        banheiros = st.number_input("Banheiros", min_value=0, step=1, value=(st.session_state.ads[st.session_state.selected_ad]['bath_rooms'] if st.session_state.selected_ad is not None else 0))
        suites = st.number_input("Suítes", min_value=0, step=1, value=(st.session_state.ads[st.session_state.selected_ad]['suites'] if st.session_state.selected_ad is not None else 0))
        caracteristicas = st.text_input("Características (separadas por vírgula)", value=(", ".join(st.session_state.ads[st.session_state.selected_ad]['content']) if st.session_state.selected_ad is not None else ""))
        cidades = [c['nome'] for c in st.session_state.cidades]
        anunciantes = [a['nome'] for a in st.session_state.anunciantes]
        cidade_sel = st.selectbox("Cidade", options=[""]+cidades)
        ann_sel = st.selectbox("Anunciante", options=[""]+anunciantes)
        if st.form_submit_button(mode):
            ad = {"titulo": titulo, "descricao": descricao, "preco": preco, "area": area,
                  "quartos": quartos, "banheiros": banheiros, "suites": suites,
                  "caracteristicas": [c.strip() for c in caracteristicas.split(",") if c.strip()],
                  "cidade": cidade_sel, "anunciante": ann_sel}
            if st.session_state.selected_ad is None:
                st.session_state.ads.append(ad)
                st.success("Anúncio criado com sucesso!")
            else:
                st.session_state.ads[st.session_state.selected_ad] = ad
                st.success("Anúncio atualizado com sucesso!")
            st.session_state.selected_ad = None

def show_ads_list():
    st.subheader("Anúncios")
    if not st.session_state.ads:
        st.info("Nenhum anúncio cadastrado.")
        return
    for idx, ad in enumerate(st.session_state.ads):
        cols = st.columns([4,1,1])
        cols[0].markdown(f"**{ad['title']}** ({ad['city']["name"]}) - anunciante | R$ {ad['price']}")
        if cols[1].button("Editar", key=f"edit_ad_{idx}"):
            st.session_state.selected_ad = idx
            st.session_state.subpage = "Adicionar"   # <<< aqui!
            st.experimental_rerun()
        if cols[2].button("Excluir", key=f"del_ad_{idx}"):
            delete_ad(idx)
            st.success("Anúncio excluído")

# CRUD Cidades
def city_form():
    mode = "Editar" if st.session_state.selected_city is not None else "Criar"
    with st.form(key="city_form"):
        st.subheader(f"{mode} Cidade")
        nome = st.text_input("Nome", value=(st.session_state.cidades[st.session_state.selected_city]['nome'] if st.session_state.selected_city is not None else ""))
        estado = st.text_input("Estado", value=(st.session_state.cidades[st.session_state.selected_city]['estado'] if st.session_state.selected_city is not None else ""))
        if st.form_submit_button(mode):
            city = {"nome": nome, "estado": estado}
            if st.session_state.selected_city is None:
                st.session_state.cidades.append(city)
                st.success("Cidade criada!")
            else:
                st.session_state.cidades[st.session_state.selected_city] = city
                st.success("Cidade atualizada!")
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
        if cols[2].button("Excluir", key=f"del_city_{idx}"):
            st.session_state.cidades.pop(idx)
            st.success("Cidade excluída")

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
        if cols[2].button("Excluir", key=f"del_ann_{idx}"):
            st.session_state.anunciantes.pop(idx)
            st.success("Anunciante excluído")

# Roteamento de páginas
if st.session_state.page == "App":
    st.title("Dakila IA")
    st.caption("Interface de comunicação para a Dakila IA")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"}]
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Digite sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = get_llm_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.markdown(response)
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
