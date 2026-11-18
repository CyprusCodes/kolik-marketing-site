const form = document.querySelector("[data-kolik-form]");

if (form) {
  const english = document.documentElement.lang === "en";
  const feedback = form.querySelector(".form-feedback");
  const submit = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submit.disabled) return;

    const payload = Object.fromEntries(new FormData(form));
    submit.disabled = true;
    feedback.textContent = "";
    feedback.removeAttribute("data-error");

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error("Form submission failed");
      form.reset();
      feedback.textContent = english ? "Thank you. Your request was sent." : "Teşekkürler, talebiniz gönderildi.";
    } catch {
      feedback.setAttribute("data-error", "");
      feedback.textContent = english ? "We couldn’t send your request. Please try again." : "Gönderilemedi. Lütfen tekrar deneyin.";
    } finally {
      submit.disabled = false;
    }
  });
}
