(function () {
  const tokenCard = document.querySelector("[data-api-token-card]");
  if (!tokenCard) {
    return;
  }

  const generateButton = tokenCard.querySelector(".admin-home-api-card__generate");
  const copyButton = tokenCard.querySelector(".admin-home-api-card__copy");
  const result = tokenCard.querySelector(".admin-home-api-card__result");
  const accessTokenField = tokenCard.querySelector("[data-api-token-access]");
  const refreshTokenField = tokenCard.querySelector("[data-api-token-refresh]");
  const feedback = tokenCard.querySelector("[data-api-token-feedback]");
  const csrfInput = tokenCard.querySelector("[data-api-token-csrf]");
  const tokenUrl = tokenCard.dataset.tokenUrl;

  const setFeedback = function (message, state) {
    feedback.textContent = message;
    feedback.dataset.state = state || "";
  };

  generateButton.addEventListener("click", async function () {
    generateButton.disabled = true;
    copyButton.disabled = true;
    setFeedback("Generando token...", "loading");

    try {
      const response = await fetch(tokenUrl, {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrfInput.value,
        },
        credentials: "same-origin",
        body: "{}",
      });

      if (!response.ok) {
        throw new Error("No se pudo generar el token.");
      }

      const payload = await response.json();
      accessTokenField.value = payload.access || "";
      refreshTokenField.value = payload.refresh || "";
      result.hidden = false;
      copyButton.disabled = !payload.access;
      setFeedback("Token generado correctamente.", "success");
    } catch (error) {
      setFeedback(error.message, "error");
    } finally {
      generateButton.disabled = false;
    }
  });

  copyButton.addEventListener("click", async function () {
    if (!accessTokenField.value) {
      return;
    }

    try {
      await navigator.clipboard.writeText(accessTokenField.value);
      setFeedback("Access token copiado.", "success");
    } catch (error) {
      accessTokenField.select();
      setFeedback("Selecciona y copia el token manualmente.", "error");
    }
  });
})();
