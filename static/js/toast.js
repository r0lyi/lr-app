(function () {
  function closeToast(toast) {
    if (!toast || !toast.isConnected) return;
    toast.classList.remove("is-visible");
    setTimeout(function () {
      if (toast && toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 420);
  }

  function initToast(toast) {
    if (!toast || toast.dataset.ready === "1") return;

    toast.dataset.ready = "1";
    var duration = parseInt(toast.dataset.duration || "5000", 10);

    if (!isNaN(duration) && duration > 0) {
      toast.style.setProperty("--toast-duration", duration + "ms");
      setTimeout(function () {
        closeToast(toast);
      }, duration);
    }

    var closeButton = toast.querySelector("[data-toast-close]");
    if (closeButton) {
      closeButton.addEventListener("click", function () {
        closeToast(toast);
      });
    }

    requestAnimationFrame(function () {
      toast.classList.add("is-visible");
    });
  }

  function initToasts(root) {
    var scope = root || document;
    var toasts = scope.querySelectorAll("[data-ui-toast]");
    for (var i = 0; i < toasts.length; i++) {
      initToast(toasts[i]);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initToasts(document);
  });

  document.body.addEventListener("htmx:afterSwap", function (event) {
    initToasts(event.detail?.target || document);
  });
})();