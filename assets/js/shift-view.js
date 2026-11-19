const rota = document.querySelector(".rota");

if (rota) {
  const switcher = rota.querySelector(".rota-switch");
  const buttons = [...switcher.querySelectorAll("button")];

  function show(view) {
    rota.dataset.view = view;
    buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.view === view)));
  }

  switcher.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (button) show(button.dataset.view);
  });

  show("manager");
  switcher.hidden = false;
}
