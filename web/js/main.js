(() => {
  "use strict";
  const button = document.querySelector("[data-copy-target]");
  if (!button) return;
  button.addEventListener("click", async () => {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const original = button.textContent;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(target.textContent.trim());
      button.textContent = "Copied ✓";
    } catch {
      button.textContent = "Select command to copy";
      const selection = window.getSelection();
      if (selection) {
        const range = document.createRange();
        range.selectNodeContents(target);
        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
    window.setTimeout(() => { button.textContent = original; }, 2200);
  });
})();
