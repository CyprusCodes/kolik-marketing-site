const header = document.querySelector(".site-header");
const menuToggle = header?.querySelector(".menu-toggle");

if (menuToggle) {
  const compact = window.matchMedia("(max-width: 52rem)");

  function setMenu(open) {
    header.dataset.menu = open ? "open" : "closed";
    menuToggle.setAttribute("aria-expanded", String(open));
  }

  setMenu(false);
  menuToggle.addEventListener("click", () => setMenu(header.dataset.menu === "closed"));
  compact.addEventListener("change", () => setMenu(false));

  header.addEventListener("click", (event) => {
    if (event.target.closest(".primary-nav a[href]")) setMenu(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && header.dataset.menu === "open" && !document.querySelector(".platform-menu[open]")) {
      setMenu(false);
      menuToggle.focus();
    }
  });
}

const platformMenu = document.querySelector(".platform-menu");

if (platformMenu) {
  const summary = platformMenu.querySelector("summary");
  const groups = [...platformMenu.querySelectorAll(".platform-group")];
  const desktop = window.matchMedia("(min-width: 52.01rem)");

  function updateGroups() {
    groups.forEach((group) => {
      group.open = desktop.matches;
      group.querySelector("summary").tabIndex = desktop.matches ? -1 : 0;
    });
  }

  platformMenu.dataset.adapted = "";
  updateGroups();
  desktop.addEventListener("change", updateGroups);

  document.addEventListener("click", (event) => {
    if (!platformMenu.contains(event.target)) platformMenu.open = false;
  });

  platformMenu.addEventListener("click", (event) => {
    if (desktop.matches && event.target.closest(".platform-group > summary") && !event.target.closest("a[href]")) {
      event.preventDefault();
    }
    if (event.target.closest("a[href]")) {
      platformMenu.open = false;
      summary.focus();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && platformMenu.open) {
      platformMenu.open = false;
      summary.focus();
    }
  });
}
