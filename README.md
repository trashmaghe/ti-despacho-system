# Controle TI - v2

Sistema Flask para controle de recebimento e despacho de computadores, com interface escura inspirada em produtos modernos como Railway e módulo administrativo de usuários.

## Novidades da v2

- visual dark mais profissional
- gerenciamento de usuários
- criação e edição de usuários
- ativação e desativação de acessos
- tela de minha conta com troca de senha
- atualização automática simples do banco para colunas novas de usuários

## Variáveis de ambiente

```env
SECRET_KEY=sua-chave-forte
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-a-senha
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
DATABASE_URL=postgresql://...
```

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
python run.py
```

## Railway

Start command:

```bash
gunicorn -b 0.0.0.0:$PORT run:app
```

Variáveis recomendadas:

```env
SECRET_KEY=sua-chave-forte
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-a-senha
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
DATABASE_URL=${{Postgres.DATABASE_URL}}
```
