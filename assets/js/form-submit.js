const form = document.querySelector("[data-kolik-form]");

if (form) {
  const english = document.documentElement.lang === "en";
  const feedback = form.querySelector(".form-feedback");
  const submit = form.querySelector('button[type="submit"]');
  const started = Date.now();
  const messages = english
    ? { sent: "Thank you. Your request was sent.", failed: "We couldn’t send your request. Please try again." }
    : { sent: "Teşekkürler, talebiniz gönderildi.", failed: "Gönderilemedi. Lütfen tekrar deneyin." };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submit.disabled) return;

    const body = new URLSearchParams(new FormData(form));
    body.set("form", form.dataset.kolikForm);
    body.set("lang", english ? "en" : "tr");
    body.set("page", window.location.pathname);
    body.set("started", String(started));

    submit.disabled = true;
    feedback.textContent = "";
    feedback.removeAttribute("data-error");

    try {
      const response = await fetch(form.action, { method: "POST", body });
      const result = await response.json();
      if (!result.ok) throw new Error(result.error || "Form submission failed");
      form.reset();
      feedback.textContent = messages.sent;
    } catch {
      feedback.setAttribute("data-error", "");
      feedback.textContent = messages.failed;
    } finally {
      submit.disabled = false;
    }
  });
}
