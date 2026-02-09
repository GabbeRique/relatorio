import streamlit as st
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ARQUIVO = "processos.json"

# =========================
# DADOS
# =========================
def carregar():
    if not os.path.exists(ARQUIVO):
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# =========================
# GERAR PDF REAL
# =========================
def gerar_pdf(dados):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    y = altura - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Relatórios / Processos")

    y -= 30
    c.setFont("Helvetica", 11)

    for i, rel in enumerate(dados, 1):
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = altura - 40

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, f"{i}. {rel['nome']}")
        y -= 18

        c.setFont("Helvetica", 11)
        for j, passo in enumerate(rel["passos"], 1):
            if y < 80:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = altura - 40

            c.drawString(60, y, f"{j}. {passo}")
            y -= 14

        y -= 10

    c.save()
    buffer.seek(0)
    return buffer

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Relatórios",
    page_icon="📋",
    layout="centered"
)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp { background-color: #0f172a; }

div[data-testid="stExpander"] {
    border-radius: 12px;
    border: 1px solid #1e293b;
    background: #020617;
}

div[data-testid="stExpander"] summary {
    padding: 10px 14px !important;
    font-size: 14px !important;
    font-weight: 600;
    color: #93c5fd;
}

div[data-testid="stExpander"] > div {
    padding: 10px 14px 14px 14px !important;
}

.passo {
    background: #020617;
    border: 1px solid #1e293b;
    padding: 6px 10px;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 14px;
    color: #e5e7eb;
}

.info {
    font-size: 13px;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.title("📋 Relatórios / Processos")

dados = carregar()

# =========================
# EXPORTAR
# =========================
st.markdown("### ⬇️ Exportar")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "📄 Baixar JSON",
        data=json.dumps(dados, indent=2, ensure_ascii=False),
        file_name="processos.json",
        mime="application/json"
    )

with col2:
    st.download_button(
        "🧾 Baixar PDF",
        data=gerar_pdf(dados),
        file_name="relatorios.pdf",
        mime="application/pdf"
    )

# =========================
# NOVO RELATÓRIO
# =========================
with st.expander("➕ Novo relatório"):
    with st.form("novo_relatorio"):
        nome = st.text_input(
            "",
            placeholder="Nome do relatório",
            label_visibility="collapsed"
        )
        criar = st.form_submit_button("Criar")

        if criar and nome.strip():
            dados.append({"nome": nome.strip(), "passos": []})
            salvar(dados)
            st.rerun()

# =========================
# RELATÓRIOS
# =========================
for idx, relatorio in enumerate(dados):

    with st.expander(f"{idx+1}. {relatorio['nome']}", expanded=False):

        col_t, col_del = st.columns([6, 1])
        with col_del:
            if st.button("🗑", key=f"del_rel_{idx}"):
                dados.pop(idx)
                salvar(dados)
                st.rerun()

        if relatorio["passos"]:
            for i, passo in enumerate(relatorio["passos"]):
                col1, col2 = st.columns([12, 1])

                with col1:
                    st.markdown(
                        f"<div class='passo'>{i+1}. {passo}</div>",
                        unsafe_allow_html=True
                    )

                with col2:
                    if st.button("❌", key=f"del_passo_{idx}_{i}"):
                        relatorio["passos"].pop(i)
                        salvar(dados)
                        st.rerun()
        else:
            st.markdown(
                "<div class='info'>Nenhum passo cadastrado</div>",
                unsafe_allow_html=True
            )

        with st.form(f"add_passo_{idx}"):
            novo_passo = st.text_input(
                "",
                placeholder="Adicionar passo",
                label_visibility="collapsed"
            )
            add = st.form_submit_button("➕")

            if add and novo_passo.strip():
                relatorio["passos"].append(novo_passo.strip())
                salvar(dados)
                st.rerun()
