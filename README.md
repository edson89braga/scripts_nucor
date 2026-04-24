# Calculadora de Ociosidade — Correição Disciplinar

Ferramenta interna de RH para calcular dias de afastamento formal que se sobrepõem ao prazo de execução de um trabalho.

---

## Estrutura dos arquivos

```
.
├── app.py              # Aplicação Streamlit (lógica + interface)
├── requirements.txt    # Dependências Python
├── Dockerfile          # Imagem Docker
├── docker-compose.yml  # Orquestração do container
└── README.md
```

---

## Como executar

### Opção 1 — Docker Compose (recomendado)

```bash
# Construir e subir o container
docker compose up --build -d

# Acessar no navegador
http://localhost:8501

# Parar o container
docker compose down
```

### Opção 2 — Docker puro

```bash
# Build
docker build -t calculadora-prazos-cruzamentos .

# Run
docker run -d -p 8501:8501 --name calculadora-prazos-cruzamentos calculadora-prazos-cruzamentos

# Parar
docker stop calculadora-prazos-cruzamentos && docker rm calculadora-prazos-cruzamentos
```

### Opção 3 — Local (sem Docker)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Regras de negócio aplicadas

| Regra | Detalhe |
|---|---|
| Prazo do trabalho | Não inclusivo no início, inclusivo no fim |
| Período de afastamento | Inclusivo em ambas as pontas |
| Múltiplos afastamentos | Ordenados e mesclados (sobrepostos/adjacentes) |
| Interseção | Apenas dias dentro do prazo são contabilizados |

### Exemplo

- Prazo: `10/01/2020` a `20/01/2020` → 10 dias úteis de prazo
- Afastamento: `10/01/2020` a `15/01/2020` → 6 dias (inclusivo)
- Interseção: 6 dias (o dia 10/01 está no afastamento, mas fora do prazo por ser não-inclusivo)
- **Output: 6**

---

## Formato de entrada esperado

O sistema usa **regex** para extrair datas no formato `dd/mm/aaaa`. Pode-se colar texto livre — o parser localiza os pares de datas automaticamente.

**Prazo do trabalho** — deve conter exatamente 2 datas:
```
Prazo concedido para conclusão: 10/01/2020 a 20/01/2020.
```

**Afastamentos** — pode conter múltiplos pares:
```
Licença médica: 10/01/2020 a 15/01/2020
Férias regulamentares: 01/03/2020 a 20/03/2020
```
