import re
import streamlit as st
from datetime import date, timedelta
from typing import Optional

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculadora cruzamento entre períodos",
    page_icon="⚖️",
    layout="centered",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Fundo geral */
.stApp {
    background-color: #F5F4F0;
}

/* Cabeçalho customizado */
.header-block {
    background-color: #1A1A2E;
    color: #E8E4D9;
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 4px;
    margin-bottom: 2rem;
    border-left: 6px solid #C9A84C;
}
.header-block h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0 0 0.4rem 0;
    letter-spacing: 0.04em;
    color: #E8E4D9;
}
.header-block p {
    font-size: 0.85rem;
    color: #9A9480;
    margin: 0;
    line-height: 1.5;
}

/* Labels */
.field-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4A4635;
    margin-bottom: 0.3rem;
    display: block;
}

/* Áreas de texto */
textarea {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    background-color: #FDFCF8 !important;
    border: 1.5px solid #D4D0C4 !important;
    border-radius: 3px !important;
    color: #2C2A20 !important;
}
textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.18) !important;
}

/* Botão principal */
.stButton > button {
    background-color: #1A1A2E !important;
    color: #E8E4D9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.65rem 2.5rem !important;
    transition: background 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background-color: #C9A84C !important;
    color: #1A1A2E !important;
}

/* Card de resultado */
.result-card {
    background-color: #1A1A2E;
    border-left: 6px solid #C9A84C;
    border-radius: 4px;
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
    text-align: center;
}
.result-card .result-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 4rem;
    font-weight: 600;
    color: #C9A84C;
    line-height: 1;
    display: block;
}
.result-card .result-label {
    font-size: 0.8rem;
    color: #9A9480;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    display: block;
    font-family: 'IBM Plex Mono', monospace;
}

/* Card de detalhamento */
.detail-card {
    background-color: #FDFCF8;
    border: 1.5px solid #D4D0C4;
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #4A4635;
    line-height: 1.8;
}
.detail-card strong {
    color: #1A1A2E;
}

/* Erro */
.error-box {
    background-color: #FDF2F2;
    border: 1.5px solid #E8AAAA;
    border-radius: 3px;
    padding: 1rem 1.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: #8B2020;
    margin-top: 1rem;
}

/* Aviso */
.warn-box {
    background-color: #FFFBF0;
    border: 1.5px solid #E8D080;
    border-radius: 3px;
    padding: 0.8rem 1.2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #7A6010;
    margin-top: 0.5rem;
}

/* Divisor */
hr.custom {
    border: none;
    border-top: 1.5px solid #D4D0C4;
    margin: 1.5rem 0;
}

/* Oculta footer padrão do Streamlit */
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Lógica de negócio ─────────────────────────────────────────────────────────

DATE_PATTERN = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")


def extrair_datas(texto: str) -> list[date]:
    """Extrai todas as datas no formato dd/mm/aaaa de um texto."""
    matches = DATE_PATTERN.findall(texto)
    datas = []
    for dia, mes, ano in matches:
        try:
            datas.append(date(int(ano), int(mes), int(dia)))
        except ValueError:
            pass  # data inválida — ignora
    return datas


def extrair_prazo(texto: str) -> Optional[tuple[date, date]]:
    """Retorna (início, fim) do prazo a partir do texto."""
    datas = extrair_datas(texto)
    if len(datas) < 2:
        return None
    return datas[0], datas[1]


def extrair_afastamentos(texto: str) -> list[tuple[date, date]]:
    """
    Extrai pares de datas consecutivos do texto como períodos de afastamento.
    Pares: (data[0], data[1]), (data[2], data[3]), …
    """
    datas = extrair_datas(texto)
    periodos = []
    for i in range(0, len(datas) - 1, 2):
        inicio, fim = datas[i], datas[i + 1]
        if inicio > fim:
            inicio, fim = fim, inicio  # tolera inversão
        periodos.append((inicio, fim))
    return periodos


def normalizar_periodos(periodos: list[tuple[date, date]]) -> list[tuple[date, date]]:
    """Ordena e mescla períodos sobrepostos ou adjacentes."""
    if not periodos:
        return []
    ordenados = sorted(periodos, key=lambda p: p[0])
    merged = [ordenados[0]]
    for inicio, fim in ordenados[1:]:
        ult_inicio, ult_fim = merged[-1]
        # Adjacente: fim anterior + 1 dia == início atual
        if inicio <= ult_fim + timedelta(days=1):
            merged[-1] = (ult_inicio, max(ult_fim, fim))
        else:
            merged.append((inicio, fim))
    return merged


def dias_afastamento_no_prazo(
    prazo_inicio: date,
    prazo_fim: date,
    periodos_norm: list[tuple[date, date]],
) -> tuple[int, list[dict]]:
    """
    Calcula os dias de afastamento que caem dentro do prazo do trabalho.

    Regras:
      - Prazo (contagem de dias de ociosidade): NÃO inclusivo no início, inclusivo no fim.
        → dias de prazo = (prazo_fim - prazo_inicio).days
      - Para fins de INTERSEÇÃO com afastamentos, a janela do prazo é [prazo_inicio, prazo_fim]
        (ambos inclusivos), pois um afastamento que se inicia no mesmo dia do prazo deve ser
        descontado (o funcionário estava afastado desde o recebimento da tarefa).
      - Afastamento: inclusivo em ambas as pontas.

    Interseção de [af_inicio, af_fim] com [prazo_inicio, prazo_fim]:
      overlap_inicio = max(af_inicio, prazo_inicio)
      overlap_fim    = min(af_fim, prazo_fim)
      dias = (overlap_fim - overlap_inicio).days + 1  se overlap_fim >= overlap_inicio
    """
    total = 0
    detalhes = []
    for af_inicio, af_fim in periodos_norm:
        overlap_inicio = max(af_inicio, prazo_inicio)
        overlap_fim = min(af_fim, prazo_fim)
        if overlap_fim >= overlap_inicio:
            dias = (overlap_fim - overlap_inicio).days + 1
        else:
            dias = 0
        detalhes.append({
            "af_inicio": af_inicio,
            "af_fim": af_fim,
            "overlap_inicio": overlap_inicio if dias > 0 else None,
            "overlap_fim": overlap_fim if dias > 0 else None,
            "dias": dias,
        })
        total += dias
    return total, detalhes


def formatar_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# ── Interface ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-block">
  <h1>⚖️ CALCULADORA CRUZAMENTO PERÍODOS</h1>
  <p>Correição disciplinar — desconto de afastamentos formais sobre o prazo do trabalho</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown('<span class="field-label">Prazo do trabalho</span>', unsafe_allow_html=True)
    texto_prazo = st.text_area(
        label="prazo",
        placeholder="Cole aqui o trecho com as datas de início e fim do prazo.\nEx.: Prazo concedido: 10/01/2020 a 20/01/2020.",
        height=140,
        label_visibility="collapsed",
        key="prazo",
    )

with col2:
    st.markdown('<span class="field-label">Afastamentos formais</span>', unsafe_allow_html=True)
    texto_afastamentos = st.text_area(
        label="afastamentos",
        placeholder="Cole aqui os períodos de afastamento.\nEx.:\nLicença médica: 10/01/2020 a 15/01/2020\nFérias: 01/03/2020 a 20/03/2020",
        height=140,
        label_visibility="collapsed",
        key="afastamentos",
    )

processar = st.button("▶  CALCULAR DIAS DESCONTÁVEIS", use_container_width=True)

if processar:
    erros = []

    # Extração do prazo
    prazo = extrair_prazo(texto_prazo) if texto_prazo.strip() else None
    if not prazo:
        erros.append("Não foi possível extrair duas datas do campo <strong>Prazo do trabalho</strong>. Verifique o formato dd/mm/aaaa.")

    # Extração dos afastamentos
    periodos_brutos = extrair_afastamentos(texto_afastamentos) if texto_afastamentos.strip() else []
    sem_afastamentos = len(periodos_brutos) == 0 and texto_afastamentos.strip() != ""

    if erros:
        for e in erros:
            st.markdown(f'<div class="error-box">⚠ {e}</div>', unsafe_allow_html=True)
    else:
        if not prazo:
            raise Exception("Não foi possível extrair o prazo.")
        
        prazo_inicio, prazo_fim = prazo

        if prazo_inicio >= prazo_fim:
            st.markdown('<div class="error-box">⚠ A data de início do prazo deve ser anterior à data de fim.</div>', unsafe_allow_html=True)
        else:
            dias_prazo = (prazo_fim - prazo_inicio).days  # não inclusivo no início

            periodos_norm = normalizar_periodos(periodos_brutos)
            total_dias, detalhes = dias_afastamento_no_prazo(prazo_inicio, prazo_fim, periodos_norm)

            # ── Resultado ──────────────────────────────────────────────────
            st.markdown(f"""
            <div class="result-card">
              <span class="result-number">{total_dias}</span>
              <span class="result-label">dias de afastamento descontáveis</span>
            </div>
            """, unsafe_allow_html=True)

            # ── Detalhamento ───────────────────────────────────────────────
            linhas_afastamento = ""
            if periodos_norm:
                for d in detalhes:
                    af_str = f"{formatar_data(d['af_inicio'])} → {formatar_data(d['af_fim'])}"
                    if d["dias"] > 0:
                        ov_str = f"{formatar_data(d['overlap_inicio'])} → {formatar_data(d['overlap_fim'])}"
                        linhas_afastamento += (
                            f"  {af_str}  &nbsp;|&nbsp; "
                            f"interseção: {ov_str} &nbsp;→&nbsp; "
                            f"<strong>{d['dias']} dia(s)</strong><br>"
                        )
                    else:
                        linhas_afastamento += (
                            f"  {af_str}  &nbsp;|&nbsp; "
                            f"<em>fora do prazo — 0 dias</em><br>"
                        )
            else:
                linhas_afastamento = "  <em>Nenhum afastamento informado.</em>"

            st.markdown(f"""
            <div class="detail-card">
              <strong>PRAZO DO TRABALHO</strong><br>
              &nbsp;&nbsp;{formatar_data(prazo_inicio)} (não inclusivo) → {formatar_data(prazo_fim)} (inclusivo)
              &nbsp;= <strong>{dias_prazo} dia(s)</strong><br>
              <br>
              <strong>AFASTAMENTOS (após normalização)</strong><br>
              {linhas_afastamento}
              <br>
              <strong>TOTAL DESCONTÁVEL &nbsp;→&nbsp; {total_dias} dia(s)</strong>
            </div>
            """, unsafe_allow_html=True)

            if sem_afastamentos:
                st.markdown('<div class="warn-box">⚠ Nenhum par de datas encontrado no campo de afastamentos.</div>', unsafe_allow_html=True)

            if periodos_brutos != periodos_norm:
                st.markdown('<div class="warn-box">ℹ Períodos sobrepostos ou adjacentes foram mesclados automaticamente.</div>', unsafe_allow_html=True)

# >>> streamlit run app.py
