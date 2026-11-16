---
name: django-validation
description: Verifica alterações no sistema Django e prepara uma publicação segura.
---

# Validação e publicação

- Execute `python manage.py check` e `python manage.py test` após mudanças de aplicação.
- Confira o resultado completo; não informe validação que não foi executada.
- Para produção, exija `DEBUG=False`, `SECRET_KEY` forte, hosts autorizados, conexão de banco e SMTP configurados por ambiente.
- Aplique migrações e execute `python manage.py collectstatic --noinput` antes do deploy.
- O deploy no App Engine exige projeto Google Cloud, faturamento, SDK autenticado e configuração externa; nunca invente um link de produção.
- A atividade de conhecimento do TestAI é realizada na plataforma pelo aluno e não pode ser simulada no código.
