# Orientações para agentes de IA

## Contexto

- Projeto Django em português para vitrine, pedidos e encomendas de uma padaria.
- O app principal é `confeitaria`; as configurações ficam em `nucleo/settings.py`.
- Os nomes de campos, URLs, templates e mensagens seguem o português já usado no projeto.

## Regras para alterações

- Leia os arquivos relacionados antes de editar e mantenha as mudanças limitadas à tarefa.
- `Pedido` e `Encomenda` pertencem ao usuário em `cliente`. Listas, detalhes, edição e exclusão devem sempre filtrar pelo usuário autenticado, sem exceção para `is_staff`.
- Ao criar pedidos ou encomendas, preencha `cliente` no servidor com `request.user`; nunca aceite esse campo do formulário.
- Use Django Forms, CBVs e templates existentes. Preserve CSRF e mensagens de erro/sucesso.
- Crie migrações quando alterar modelos e não edite migrações aplicadas para esconder mudanças de esquema.
- Não inclua `.env`, `.env.*`, senhas, chaves, dados do banco ou credenciais nos commits, prompts ou arquivos enviados a serviços externos.
- Para enviar e-mail em produção, configure o backend SMTP por variáveis de ambiente; o backend de console é apenas para desenvolvimento.
- Bibliotecas de interface externas são carregadas por CDN no layout base. Mantenha inicialização e uso dos plugins em `confeitaria/static/confeitaria/js/site.js`.

## Verificação

1. Instale as dependências de `requirements.txt`.
2. Execute `python manage.py check`.
3. Execute `python manage.py test`.
4. Antes de publicar no App Engine, confira as variáveis secretas, aplique as migrações e gere os arquivos estáticos.
5. A validação externa da plataforma TestAI é manual e depende de acesso do aluno.

## Preparação do Gitingest

Configure Include com `*.py, *.md, *.js, *form.html, *list.html` e acrescente os padrões/arquivos usados neste projeto: `*formulario.html`, `*lista.html`, `base.html`, `entrar.html`, `recuperar_*.html`, `redefinir_senha.html`, `senha_*.html`, `email_recuperar_senha.txt`, `assunto_recuperar_senha.txt`, `estilo.css`, `requirements.txt` e `app.yaml`.

Não inclua `.env`, `.env.*`, `venv/`, `staticfiles/`, arquivos `.pyc` ou dados/arquivos do banco.
