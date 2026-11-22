(() => {
  const root = document.querySelector(".home-assistant");
  if (!root) return;
  const buttons = [...root.querySelectorAll(".home-assistant-chips button")];
  const body = root.querySelector(".home-chat-body");
  if (!buttons.length || !body) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let timer;

  const show = (button) => {
    clearTimeout(timer);
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b === button)));

    const question = document.createElement("p");
    question.className = "home-chat-q";
    question.textContent = button.textContent;

    const answer = document.createElement("div");
    answer.className = "home-chat-a";
    answer.innerHTML = `<p>${button.dataset.answer}</p><span class="home-chat-action"></span>`;
    answer.querySelector(".home-chat-action").textContent = button.dataset.action;

    if (reduce) {
      body.replaceChildren(question, answer);
      return;
    }
    const typing = document.createElement("div");
    typing.className = "home-chat-typing";
    typing.innerHTML = "<i></i><i></i><i></i>";
    body.replaceChildren(question, typing);
    timer = setTimeout(() => body.replaceChildren(question, answer), 700);
  };

  buttons.forEach((button) => button.addEventListener("click", () => show(button)));
})();
