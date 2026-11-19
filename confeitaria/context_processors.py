def grupos_do_usuario(request):
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {"usuario_equipe": False}
    return {"usuario_equipe": usuario.groups.filter(name="Equipe").exists()}
