(function () {
  var modal = document.getElementById("password-modal");
  if (!modal) {
    return;
  }

  var openButtons = document.querySelectorAll(
    "[data-password-modal-open], #open-password-modal"
  );
  var closeButtons = modal.querySelectorAll(
    "[data-password-modal-close], .profile-modal-cancel"
  );
  var overlay = modal.querySelector(".ui-modal__overlay");
  var initialFocus =
    modal.querySelector('.profile-modal__form input:not([type="hidden"])') ||
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

  openButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      openModal();
    });
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      closeModal();
    });
  });

  if (overlay) {
    overlay.addEventListener("click", function () {
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
