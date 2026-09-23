# Agente de Conhecimento

Protótipo de RAG (Retrieval-Augmented Generation): upload de documentos
(`.txt`/`.pdf`), busca vetorial e chat com citação de fontes. Interface em
inglês, português e italiano.

**Stack:** Next.js (App Router) + TypeScript · FastAPI + Python · PostgreSQL
com `pgvector` · OpenAI (chat + embeddings)

## Como rodar

### Com Docker (recomendado)

1. Copie o template de variáveis de ambiente e preencha sua chave da OpenAI:

   ```bash
   cp backend/.env.example backend/.env
   # edite backend/.env e defina OPENAI_API_KEY
   ```

2. Faça o build das imagens e suba tudo:

   ```bash
   docker compose build
   docker compose up -d
   ```

3. Acesse **http://localhost:3000**. A API fica em `http://localhost:8000`.

### Sem Docker (desenvolvimento)

Backend — requer [uv](https://docs.astral.sh/uv/) e um Postgres com a
extensão `vector` disponível:

```bash
cd backend
cp .env.example .env   # ajuste OPENAI_API_KEY e DATABASE_URL
uv run fastapi dev main.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

### Testes e lint (backend)

```bash
cd backend
uv run pytest
uv run ruff check .
```

## Decisões de arquitetura

- **RAG simples, sem framework de RAG**: chunking por tamanho fixo (1000
  caracteres, overlap de 150), embeddings via OpenAI, busca por similaridade
  de cosseno direto no Postgres/`pgvector` (sem índice aproximado — o volume
  de um protótipo não justifica). O LLM cita os trechos usados e o frontend
  mostra as fontes.
- **Upload assíncrono**: o backend extrai, divide e embeda o documento em
  background; o frontend faz polling do status. Necessário porque documentos
  grandes (ex. um livro de 1200 páginas) geram mais trechos do que a API de
  embeddings aceita numa única chamada — os embeddings são pedidos em lotes.
- **Backend em camadas** (`backend/app/`): domínio → repositórios (interface
  + implementação Postgres) → providers (OpenAI) → serviços → API. Cada
  camada é injetada via construtor, então os serviços são testáveis com
  fakes, sem precisar de banco ou rede real (`backend/tests/`).
- **Frontend com Context + hooks, sem Redux/Zustand**: `DocumentContext` e
  `LocaleContext` seguem o mesmo padrão (hook com a lógica + Provider fino)
  para compartilhar estado sem prop drilling — suficiente para o tamanho do
  app.
- **i18n sem biblioteca de rotas**: troca de idioma é estado de cliente,
  persistido em `localStorage`. Sem URLs por idioma (`/en`, `/pt`) porque é
  uma página única sem necessidade de SEO multi-idioma — uma lib como
  `next-intl` adicionaria roteamento/middleware sem benefício real aqui.
- **Sem ferramenta de migration**: mudanças de schema são
  `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` rodadas no startup. Simples e
  suficiente para um protótipo de um único dev; Alembic entraria se
  precisássemos de rollback ou histórico de schema entre ambientes.
- **Sem fila de tarefas (Celery/Redis)**: o processamento do upload roda como
  background task do próprio FastAPI. Funciona bem pro estágio atual, mas tem
  duas limitações reais: se o processo cair no meio de um upload, o documento
  fica preso em "processando" pra sempre (sem retry automático), e não há
  como limitar quantos uploads pesados rodam ao mesmo tempo. Celery (ou RQ)
  com Redis resolveria os dois — worker separado, fila persistente que
  sobrevive a um restart, retry com backoff — mas é infraestrutura extra
  (broker + processo de worker) que só compensa quando esse limite virar
  problema de verdade. Fica como próximo item de backlog, não como decisão
  descartada.
- **Multi-tenant ainda não implementado**: as tabelas não têm coluna de
  tenant/usuário; é o próximo passo natural, mas fora do escopo atual.

## Estrutura

```
frontend/   Next.js — app/, components/, hooks/, context/, i18n/, lib/
backend/    FastAPI — app/{domain,repositories,providers,services,api}/, tests/
docker-compose.yml   sobe frontend + backend + Postgres/pgvector
```
