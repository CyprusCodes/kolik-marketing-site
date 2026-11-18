const explorer = document.querySelector("[data-module-explorer]");

if (explorer) {
  const tabs = [...explorer.querySelectorAll("[data-module-tab]")];
  const panels = tabs.map((tab) => document.getElementById(tab.getAttribute("aria-controls")));

  function selectTab(index, moveFocus = false) {
    tabs.forEach((tab, position) => {
      const selected = position === index;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[position].hidden = !selected;
    });
    if (moveFocus) tabs[index].focus();
  }

  const tabList = explorer.querySelector(".module-tabs");
  tabList.setAttribute("role", "tablist");
  const desktop = window.matchMedia("(min-width: 64rem)");
  function updateOrientation() {
    tabList.setAttribute("aria-orientation", desktop.matches ? "vertical" : "horizontal");
  }
  updateOrientation();
  desktop.addEventListener("change", updateOrientation);
  tabs.forEach((tab, index) => {
    tab.setAttribute("role", "tab");
    panels[index].setAttribute("role", "tabpanel");
    tab.addEventListener("click", () => selectTab(index));
    tab.addEventListener("keydown", (event) => {
      const next = {
        ArrowRight: (index + 1) % tabs.length,
        ArrowLeft: (index + tabs.length - 1) % tabs.length,
        ArrowDown: desktop.matches ? (index + 1) % tabs.length : undefined,
        ArrowUp: desktop.matches ? (index + tabs.length - 1) % tabs.length : undefined,
        Home: 0,
        End: tabs.length - 1
      }[event.key];
      if (next === undefined) return;
      event.preventDefault();
      selectTab(next, true);
    });
  });
  const categories = ["hr", "operations", "development"];
  function selectLinkedModule() {
    const index = categories.indexOf(new URLSearchParams(window.location.search).get("module"));
    selectTab(index < 0 ? 0 : index);
  }

  selectLinkedModule();
  window.addEventListener("popstate", selectLinkedModule);
  tabList.hidden = false;
  explorer.classList.add("module-explorer-interactive");
}
