const showcase = document.querySelector(".landing-showcase");

if (showcase) {
  const picker = showcase.querySelector(".showcase-picker");
  const buttons = [...picker.querySelectorAll("button")];
  const windowFrame = showcase.querySelector(".showcase-window");
  const previews = [...windowFrame.querySelectorAll("[data-showcase-screen]")];

  picker.addEventListener("click", (event) => {
    const selected = buttons.indexOf(event.target.closest("button"));
    if (selected === -1 || buttons[selected].getAttribute("aria-pressed") === "true") return;

    buttons.forEach((button, index) => {
      const current = index === selected;
      button.setAttribute("aria-pressed", String(current));
      previews[index].hidden = !current;
    });

    windowFrame.dataset.screen = selected === 0 ? "overview" : "focused";
    windowFrame.classList.remove("is-changing");
    requestAnimationFrame(() => {
      requestAnimationFrame(() => windowFrame.classList.add("is-changing"));
    });
  });


  picker.hidden = false;
}
