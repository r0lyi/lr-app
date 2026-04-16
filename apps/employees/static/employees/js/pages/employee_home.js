(function () {
  var modal = document.getElementById("employee-delete-request-modal");
  if (!modal) {
    return;
  }

  var form = modal.querySelector("[data-vacation-delete-form]");
  var rangeNode = modal.querySelector("[data-delete-request-range]");
  var daysNode = modal.querySelector("[data-delete-request-days]");
  var openButtons = document.querySelectorAll("[data-vacation-delete-open]");
  var closeButtons = modal.querySelectorAll(
    "[data-vacation-delete-close], .employee-delete-request-modal__cancel"
  );
  var firstFocusable = modal.querySelector(".ui-modal__close");

  function syncBodyLock() {
    document.body.classList.toggle("modal-open", modal.classList.contains("is-open"));
    modal.setAttribute("aria-hidden", modal.classList.contains("is-open") ? "false" : "true");
  }

  function openModal(trigger) {
    if (!form) {
      return;
    }

    form.action = trigger.getAttribute("data-delete-url") || "";
    if (rangeNode) {
      rangeNode.textContent = trigger.getAttribute("data-request-range") || "--";
    }
    if (daysNode) {
      daysNode.textContent = trigger.getAttribute("data-request-days") || "--";
    }

    modal.classList.add("is-open");
    syncBodyLock();
    if (firstFocusable) {
      firstFocusable.focus();
    }
  }

  function closeModal() {
    modal.classList.remove("is-open");
    syncBodyLock();
    if (form) {
      form.action = "";
    }
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      openModal(button);
    });
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal.classList.contains("is-open")) {
      closeModal();
    }
  });
})();
