const form = document.querySelector("[data-kolik-form]");

// Copies the lead to Campa. Runs alongside the email, so a failure here never blocks the form.
function sendToCampa(form) {
  const url = form.dataset.campaWebhook;
  if (!url || form.elements.website?.value) return;
  const value = (name) => form.elements[name]?.value.trim() || undefined;
  const lead = {
    name: value("user-name"),
    email: value("email"),
    phone: value("phone"),
  };
  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
    keepalive: true,
  }).catch(() => {});
}

if (form) {
  const english = document.documentElement.lang === "en";
  const feedback = form.querySelector(".form-feedback");
  const submit = form.querySelector('button[type="submit"]');
  const started = Date.now();
  const email = new URLSearchParams(window.location.search).get("email");
  if (email && form.elements.email && !form.elements.email.value) form.elements.email.value = email;
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

    sendToCampa(form);

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
