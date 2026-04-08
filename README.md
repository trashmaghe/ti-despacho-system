# Controle TI - v3

Sistema Flask para controle de recebimento e despacho de computadores, agora com:

- visual v3 mais polido
- light mode e dark mode
- 4 presets de tema prontos
- arquitetura simples para criar temas novos
- gerenciamento de usuários
- fallback de banco mais seguro no Railway
- rota `/health`

## O erro do Railway que a v3 corrige

Se `DATABASE_URL` não estiver definida no Railway, a v2 podia cair para um SQLite local em caminho não gravável e gerar erro como:

```text
sqlite3.OperationalError: unable to open database file
```

Na v3:

- localmente, o fallback continua usando `instance/app.db`
- no Railway sem `DATABASE_URL`, o fallback usa `/tmp/controle-ti/app.db`
- isso evita quebrar o boot só por caminho inválido

> Ainda assim, em produção o recomendado é usar PostgreSQL no Railway para persistência real.

## Variáveis de ambiente

```env
SECRET_KEY=sua-chave-forte
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-a-senha
ADMIN_FULL_NAME=Administrador do Sistema
SYNC_ADMIN_PASSWORD_ON_STARTUP=false
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
DEFAULT_THEME_ID=railway-night
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
ADMIN_FULL_NAME=Administrador
SYNC_ADMIN_PASSWORD_ON_STARTUP=false
APP_NAME=Controle TI
ITEMS_PER_PAGE=10
DEFAULT_THEME_ID=railway-night
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## Como criar um tema novo depois

1. Abra `app/static/css/style.css`
2. Copie um bloco como `html[data-theme="railway-night"]`
3. Troque o id para algo como `html[data-theme="meu-tema"]`
4. Ajuste as variáveis de cor
5. Abra `app/theme_presets.py`
6. Adicione um novo item na lista `THEME_PRESETS`

Exemplo:

```python
{
    "id": "meu-tema",
    "name": "Meu Tema",
    "mode": "dark",
    "tag": "Custom",
    "description": "Tema criado sob medida.",
}
```

## Observação sobre senha do admin

Por padrão, mudar `ADMIN_PASSWORD` no Railway **não** sobrescreve a senha do admin já salva no banco.

Se você quiser forçar sincronização da senha definida por variável no próximo boot, use:

```env
SYNC_ADMIN_PASSWORD_ON_STARTUP=true
```

Depois do acesso voltar, pode retornar para `false`.
