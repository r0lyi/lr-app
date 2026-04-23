(function () {
  var btn = document.getElementById("dash-hamburger");
  var closeBtn = document.getElementById("dash-sidebar-close");
  var sidebar = document.querySelector(".dash-sidebar");
  var overlay = document.getElementById("dash-overlay");
  var navLinks = document.querySelectorAll(".dash-nav-link");
  var notificationsRoot = document.querySelector("[data-notifications]");
  var notificationsToggle = document.querySelector("[data-notifications-toggle]");
  var notificationsPanel = document.getElementById("dash-notifications-panel");
  var notificationsClose = document.querySelector("[data-notifications-close]");
  var helpToggle = document.querySelector("[data-help-toggle]");
  var helpPanel = document.querySelector("[data-help-panel]");
  var helpDialog = document.getElementById("dash-help-dialog");
  var helpCloseButtons = helpPanel
    ? helpPanel.querySelectorAll("[data-help-close]")
    : [];
  var helpHideTimer;
  var helpPreviousFocus;
  var setSidebarOpen = function () {};
  var setNotificationsOpen = function () {};

  if (btn && sidebar && overlay) {
    function setOpenState(open) {
      sidebar.classList.toggle("dash-sidebar--open", open);
      overlay.classList.toggle("dash-overlay--visible", open);
      btn.classList.toggle("dash-hamburger--open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("no-scroll", open);
    }

    setSidebarOpen = setOpenState;

    function toggle(open) {
      setOpenState(open);
    }

    btn.addEventListener("click", function () {
      toggle(!sidebar.classList.contains("dash-sidebar--open"));
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        toggle(false);
      });
    }

    overlay.addEventListener("click", function () {
      toggle(false);
    });

    navLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth <= 820) {
          toggle(false);
        }
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        toggle(false);
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 820) {
        setOpenState(false);
      }
    });
  }

  if (notificationsRoot && notificationsToggle && notificationsPanel) {
    setNotificationsOpen = function (open) {
      notificationsRoot.classList.toggle("dash-notifications--open", open);
      notificationsToggle.setAttribute("aria-expanded", open ? "true" : "false");
      notificationsPanel.hidden = !open;
    };

    notificationsToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      setNotificationsOpen(
        !notificationsRoot.classList.contains("dash-notifications--open")
      );
    });

    if (notificationsClose) {
      notificationsClose.addEventListener("click", function () {
        setNotificationsOpen(false);
      });
    }

    notificationsPanel.addEventListener("click", function (event) {
      event.stopPropagation();
    });

    document.addEventListener("click", function (event) {
      if (!notificationsRoot.contains(event.target)) {
        setNotificationsOpen(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        setNotificationsOpen(false);
      }
    });
  }

  if (helpToggle && helpPanel && helpDialog) {
    function getHelpFocusableElements() {
      return Array.prototype.slice
        .call(
          helpDialog.querySelectorAll(
            'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
          )
        )
        .filter(function (element) {
          return element.getClientRects().length > 0;
        });
    }

    function isHelpOpen() {
      return helpPanel.classList.contains("dash-help--open");
    }

    function setHelpOpen(open) {
      window.clearTimeout(helpHideTimer);

      if (open) {
        helpPreviousFocus = document.activeElement;
        setSidebarOpen(false);
        setNotificationsOpen(false);
        helpPanel.hidden = false;
        window.requestAnimationFrame(function () {
          helpPanel.classList.add("dash-help--open");
        });
      } else {
        helpPanel.classList.remove("dash-help--open");
        helpHideTimer = window.setTimeout(function () {
          helpPanel.hidden = true;
        }, 180);
      }

      helpPanel.setAttribute("aria-hidden", open ? "false" : "true");
      helpToggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("dash-help-open", open);

      if (open) {
        window.setTimeout(function () {
          var focusableElements = getHelpFocusableElements();
          (focusableElements[0] || helpDialog).focus();
        }, 0);
      } else if (helpPreviousFocus && typeof helpPreviousFocus.focus === "function") {
        helpPreviousFocus.focus();
        helpPreviousFocus = null;
      }
    }

    helpToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      setHelpOpen(!isHelpOpen());
    });

    helpCloseButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        setHelpOpen(false);
      });
    });

    helpPanel.addEventListener("click", function (event) {
      if (event.target === helpPanel) {
        setHelpOpen(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (!isHelpOpen()) {
        return;
      }

      if (event.key === "Escape") {
        setHelpOpen(false);
        return;
      }

      if (event.key !== "Tab") {
        return;
      }

      var focusableElements = getHelpFocusableElements();
      if (!focusableElements.length) {
        event.preventDefault();
        helpDialog.focus();
        return;
      }

      var firstFocusable = focusableElements[0];
      var lastFocusable = focusableElements[focusableElements.length - 1];

      if (event.shiftKey && document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      } else if (!event.shiftKey && document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    });
  }
})();
