(function ($) {
    "use strict";

    $(function () {
        $("[data-mask]").each(function () {
            const options = {};
            if ($(this).data("mask-reverse")) {
                options.reverse = true;
            }
            $(this).mask($(this).data("mask"), options);
        });

        $(".js-data-table").DataTable({
            paging: false,
            info: false,
            language: {
                search: "Buscar nesta página:",
                zeroRecords: "Nenhum registro encontrado nesta página",
                emptyTable: "Nenhum registro cadastrado"
            }
        });

        $(".form-exclusao").on("submit", function (event) {
            const form = this;
            if (form.dataset.confirmed === "true") {
                return;
            }

            event.preventDefault();
            $.confirm({
                title: "Confirmar exclusão",
                content: "Esta ação não pode ser desfeita.",
                buttons: {
                    cancelar: function () {},
                    excluir: {
                        btnClass: "btn-red",
                        action: function () {
                            form.dataset.confirmed = "true";
                            form.requestSubmit();
                        }
                    }
                }
            });
        });

        $(".js-sugestao").on("click", function () {
            const campo = $("#id_pergunta");
            campo.val($(this).data("texto"));
            campo.trigger("focus");
        });

        const chat = $("#chat-assistente");
        if (chat.length) {
            chat.scrollTop(chat.prop("scrollHeight"));
        }
    });
})(jQuery);
