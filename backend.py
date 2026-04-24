import re
from datetime import date, timedelta
from typing import Optional

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


