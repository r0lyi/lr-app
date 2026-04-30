(() => {
  const gettext =
    typeof window.gettext === "function" ? window.gettext : (message) => message;

  document.addEventListener("click", (event) => {
    const toggle = event.target.closest("[data-password-toggle]");
    if (!toggle) {
      return;
    }

    const field = toggle.closest("[data-password-field]");
    if (!field) {
      return;
    }

    const input = field.querySelector("[data-password-input]");
    if (!input) {
      return;
    }

    const selectionStart = input.selectionStart;
    const selectionEnd = input.selectionEnd;
    const isHidden = input.type === "password";

    input.type = isHidden ? "text" : "password";
    field.classList.toggle("is-visible", isHidden);
    toggle.setAttribute("aria-pressed", String(isHidden));
    toggle.setAttribute(
      "aria-label",
      isHidden
        ? toggle.dataset.labelHide || gettext("Ocultar contraseña")
        : toggle.dataset.labelShow || gettext("Mostrar contraseña"),
    );

    input.focus({ preventScroll: true });
    if (selectionStart !== null && selectionEnd !== null) {
      input.setSelectionRange(selectionStart, selectionEnd);
    }
  });
})();
