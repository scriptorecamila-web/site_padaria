# Contexto do projeto

Padaria Doce & Ponto é uma aplicação Django de vitrine, pedidos, encomendas, estoque e assistente.

## Aplicações

- `confeitaria` guarda produtos, pedidos, encomendas e movimentos de estoque.
- `ia` é o assistente. As conversas pertencem ao campo `usuario`.
- `nucleo` concentra `settings.py`, URLs e o entrypoint WSGI usado no App Engine.

## Regras de negócio

- `Pedido` e `Encomenda` pertencem a `cliente`. Listar, detalhar, editar e excluir filtram pelo usuário autenticado, também para quem tem `is_staff`.
- O cliente é preenchido no servidor com `request.user` e não entra no formulário.
- Salvar um pedido baixa o estoque na mesma transação. Cancelar ou excluir estorna a quantidade, sem deixar saldo negativo.
- O grupo `Clientes` acompanha usuários comuns. O grupo `Equipe` cadastra produtos e registra movimentos de estoque.
- O assistente responde com o cardápio real e, quando a pergunta é sobre pedidos ou encomendas, usa somente os registros de quem está logado.

## Integrações obrigatórias

- Autenticação: entrar, sair, alterar senha, recuperar senha por link e recuperar usuário por e-mail.
- Filtros: `confeitaria/filters.py` e `ia/filters.py`, com django-filter nas listas.
- Paginação: listas usam `paginate_by` e a tag `query_transform` em `confeitaria/templatetags/pagination_tags.py`, preservando os filtros.
- Plugins: jQuery, jQuery Mask, DataTables e jquery-confirm, carregados em `base_layout/base.html` e inicializados em `confeitaria/static/confeitaria/js/site.js`.

## Assistente e agentes

- Tela do assistente: `apps/ia/templates/assistente.html`.
- Lista de conversas: `apps/ia/templates/conversa_list.html`.
- O diretório entra em `TEMPLATES["DIRS"]` para o Django encontrar esses arquivos e para o padrão `*/ia/templates/*` incluí-los no Gitingest.
- Sem `IA_API_URL` e `IA_API_KEY`, a resposta é local. Essas variáveis ficam só no ambiente.
- Instruções de agentes: `AGENTS.md`.
- Skills: `.github/skills/` e `skills/assistente/`.

## Arquivos que a avaliação precisa enxergar

`models.py`, `views.py`, `urls.py`, `forms.py`, `filters.py`, `confeitaria/templatetags/`, `base_layout/base.html`, a tela do assistente, `nucleo/settings.py`, `AGENTS.md`, este arquivo, as pastas de skills, o app `ia`, `app.yaml` e `requirements.txt`.

Os templates de formulário, lista e detalhe terminam em `_form.html`, `_list.html` e `_detail.html`. O layout se chama `base.html` e fica em `base_layout/`.

## Gitingest

Include:

```
*.py, *.md, *.js, *.yaml, *.txt, *form.html, *list.html, *detail.html, base*.html, */ia/templates/*
```

Exclude:

```
__init__.py, admin.py, apps.py, tests.py, */migrations/*, venv/*, .venv/*, env/*, staticfiles/*, node_modules/*, *.min.js, */vendor/*, */libs/*
```

Não inclua `.env`, `.env.*`, banco, senha ou chave de API.

## Publicação

`app.yaml` sobe o serviço no Google App Engine com WhiteNoise e Gunicorn. Segredos, banco e SMTP são configurados no ambiente, não no repositório. Antes do deploy: `migrate` e `collectstatic`.
