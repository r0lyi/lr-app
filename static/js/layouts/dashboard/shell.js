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

  if (btn && sidebar && overlay) {
    function setOpenState(open) {
      sidebar.classList.toggle("dash-sidebar--open", open);
      overlay.classList.toggle("dash-overlay--visible", open);
      btn.classList.toggle("dash-hamburger--open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("no-scroll", open);
    }

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
    function setNotificationsOpen(open) {
      notificationsRoot.classList.toggle("dash-notifications--open", open);
      notificationsToggle.setAttribute("aria-expanded", open ? "true" : "false");
      notificationsPanel.hidden = !open;
    }

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
})();
