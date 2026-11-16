---
name: django-feature
description: Implementa funcionalidades Django respeitando a arquitetura e as regras de propriedade deste projeto.
---

# Funcionalidades Django

- Inspecione modelos, formulários, views, URLs, templates e testes relacionados antes de editar.
- Preserve os nomes e textos em português e reutilize as CBVs e os componentes existentes.
- `Pedido` e `Encomenda` são privados por proprietário: filtre por `request.user` em listar, detalhar, editar e excluir, mesmo para usuários `is_staff`.
- Atribua `cliente=request.user` no servidor ao criar; não exponha `cliente` em formulários.
- Use Django messages para confirmar operações, mantenha CSRF e trate erros sem esconder falhas.
- Adicione migração quando o esquema mudar e testes focados para o comportamento novo.
- Nunca coloque segredos de ambiente em código, documentação pública ou arquivos do Gitingest.
