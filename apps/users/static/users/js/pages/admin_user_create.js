(function () {
  var modal = document.getElementById("admin-user-create-modal");
  if (!modal) {
    return;
  }

  var openButton = document.getElementById("open-admin-user-create-modal");
  var closeButtons = modal.querySelectorAll(
    "[data-admin-user-create-close], .admin-user-create-modal-cancel"
  );
  var overlay = modal.querySelector(".ui-modal__overlay");
  var initialFocus =
    modal.querySelector('.admin-user-create-modal__form input:not([type="hidden"])') ||
    modal.querySelector(".ui-modal__close");

  function syncBodyLock() {
    document.body.classList.toggle("modal-open", modal.classList.contains("is-open"));
    modal.setAttribute(
      "aria-hidden",
      modal.classList.contains("is-open") ? "false" : "true"
    );
  }

  function openModal() {
    modal.classList.add("is-open");
    syncBodyLock();
    if (initialFocus) {
      window.setTimeout(function () {
        initialFocus.focus();
      }, 20);
    }
  }

  function closeModal() {
    modal.classList.remove("is-open");
    syncBodyLock();
  }

  if (openButton) {
    openButton.addEventListener("click", function () {
      openModal();
    });
  }

  if (modal.classList.contains("is-open") && initialFocus) {
    window.setTimeout(function () {
      initialFocus.focus();
    }, 20);
  }

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      event.preventDefault();
      closeModal();
    });
  });

  if (overlay) {
    overlay.addEventListener("click", function (event) {
      event.preventDefault();
      closeModal();
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal.classList.contains("is-open")) {
      closeModal();
    }
  });

  syncBodyLock();
})();
