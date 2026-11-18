const preview = document.querySelector(".assistant-preview");

if (preview) {
  const picker = preview.querySelector(".assistant-picker");
  const buttons = [...picker.querySelectorAll("button")];
  const conversations = [...preview.querySelectorAll(".assistant-messages")];

  picker.addEventListener("click", (event) => {
    const selected = buttons.indexOf(event.target.closest("button"));
    if (selected < 0) return;

    buttons.forEach((button, index) => {
      const active = index === selected;
      button.setAttribute("aria-pressed", String(active));
      conversations[index].hidden = !active;
    });
  });

  picker.hidden = false;
}
