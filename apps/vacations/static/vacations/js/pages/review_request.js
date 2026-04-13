(function () {
  document.body.classList.add("modal-open");
  window.addEventListener("pagehide", function () {
    document.body.classList.remove("modal-open");
  });
})();
