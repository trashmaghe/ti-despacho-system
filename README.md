# Controle TI - Recebimento e Despacho de Computadores

Sistema web simples para controle interno de entrada, manutenção e entrega de computadores. O projeto usa Flask, SQLAlchemy, login básico com senha hash e é compatível com deploy no Railway.

## Recursos

- Login com usuário administrador criado automaticamente
- Dashboard com indicadores
- Cadastro de recebimento de computadores
- Listagem com busca, filtros e paginação
- Edição, exclusão e visualização detalhada
- Registro de despacho / entrega
- Impressão de comprovante de recebimento e de entrega
- Exportação CSV da listagem
- Compatível com PostgreSQL no Railway e SQLite local

## Stack

- Python 3.12
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PostgreSQL / SQLite
- Gunicorn
- Bootstrap 5 por CDN

## Estrutura do projeto

```text
.
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── extensions.py
│   ├── main.py
│   ├── models.py
│   ├── utils.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── auth/login.html
│       ├── equipment/detail.html
│       ├── equipment/dispatch.html
│       ├── equipment/form.html
│       ├── equipment/list.html
│       ├── equipment/print_dispatch.html
│       ├── equipment/print_receipt.html
│       ├── errors/404.html
│       ├── errors/500.html
│       ├── base.html
│       └── dashboard.html
├── instance/
├── .env.example
├── Procfile
├── README.md
├── config.py
├── requirements.txt
├── run.py
└── runtime.txt
```

## Como rodar localmente

### 1) Criar ambiente virtual

No Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Configurar variáveis de ambiente

Copie `.env.example` para `.env` e ajuste se quiser. Para rodar localmente com SQLite, o valor padrão já funciona.

Exemplo:

```env
SECRET_KEY=sua-chave-super-segura
DATABASE_URL=sqlite:///instance/app.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
```

### 4) Iniciar a aplicação

```bash
python run.py
```

Acesse: `http://127.0.0.1:5000`

## Primeiro acesso

O sistema cria automaticamente o usuário administrador na primeira execução:

- Usuário: valor de `ADMIN_USERNAME`
- Senha: valor de `ADMIN_PASSWORD`

Troque a senha padrão antes de usar em produção.

## Banco de dados

- Em ambiente local sem `DATABASE_URL`, o sistema usa SQLite em `instance/app.db`.
- Em produção, defina `DATABASE_URL` para PostgreSQL.
- As tabelas são criadas automaticamente ao iniciar.

## Deploy no Railway

### 1) Suba o projeto para um repositório Git

```bash
git init
git add .
git commit -m "Primeira versão do Controle TI"
```

### 2) Crie um projeto no Railway

- Clique em **New Project**
- Escolha **Deploy from GitHub repo**
- Selecione o repositório deste projeto

### 3) Adicione PostgreSQL

No canvas do projeto:

- Clique em **+ New**
- Escolha **Database** → **PostgreSQL**

### 4) Configure as variáveis do serviço web

Na aba **Variables** do serviço web, configure:

```env
SECRET_KEY=gere-uma-chave-forte
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-essa-senha
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### 5) Start command

O projeto já inclui `Procfile`, mas você também pode definir manualmente:

```bash
gunicorn -b 0.0.0.0:$PORT run:app
```

### 6) Gerar domínio público

- Abra o serviço web
- Vá em **Settings** → **Networking**
- Clique em **Generate Domain**

## Variáveis de ambiente esperadas

- `SECRET_KEY`: chave da sessão Flask
- `DATABASE_URL`: string de conexão do banco
- `ADMIN_USERNAME`: usuário inicial
- `ADMIN_PASSWORD`: senha inicial
- `APP_NAME`: nome exibido na interface
- `ITEMS_PER_PAGE`: itens por página na listagem

## Regras de negócio implementadas

- Equipamento só é entregue se já existir cadastro de recebimento
- Datas de criação e atualização são salvas automaticamente
- Patrimônio e número de série ajudam na identificação
- O status é atualizado manualmente e no despacho passa para `Entregue`

## Melhorias futuras

- Controle de múltiplos usuários e perfis
- Histórico detalhado de alterações por status
- Upload de anexos e fotos
- Exportação para Excel e PDF real
- Assinatura digital em comprovantes
- API REST e auditoria
