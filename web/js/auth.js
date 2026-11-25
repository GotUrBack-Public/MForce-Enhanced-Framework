/* MForce Enhanced Framework — Firebase Authentication.
   Handles account creation and sign-in with Google, email/password and phone.
   Firebase web config is public by design; access is enforced by Firebase
   Authentication and the project's security rules, not by hiding this file.

   Firebase is loaded lazily via dynamic import so the auth module (modal UI
   + openAuthModal) always works, even if the Firebase CDN is unreachable.
   */

const firebaseConfig = {
  apiKey: "AIzaSyBXduyoX9jmwl7Whkyh2R2El-sU9SYh8Og",
  authDomain: "mforce-enhanced-framework.firebaseapp.com",
  projectId: "mforce-enhanced-framework",
  storageBucket: "mforce-enhanced-framework.firebasestorage.app",
  messagingSenderId: "318714486332",
  appId: "1:318714486332:web:134d3b6763f0c619bead39",
  measurementId: "G-7J0X46Z40T",
};

/* ---- friendly error messages ---- */
const MESSAGES = {
  "auth/invalid-credential": "Email or password is incorrect.",
  "auth/wrong-password": "Email or password is incorrect.",
  "auth/user-not-found": "Email or password is incorrect.",
  "auth/email-already-in-use": "An account with this email already exists.",
  "auth/weak-password": "Password must be at least 6 characters.",
  "auth/invalid-email": "Enter a valid email address.",
  "auth/popup-closed-by-user": "Sign-in window was closed.",
  "auth/cancelled-popup-clicked": "Sign-in was cancelled.",
  "auth/too-many-requests": "Too many attempts. Please try again later.",
  "auth/invalid-verification-code": "That verification code is not valid.",
  "auth/missing-verification-code": "Enter the verification code.",
  "auth/invalid-phone-number": "Enter a valid phone number with country code.",
  "auth/quota-exceeded": "SMS limit reached. Try again later.",
  "auth/network-request-failed": "Network error. Check your connection.",
};
const messageFor = (error) => MESSAGES[error?.code] || error?.message || "Something went wrong. Please try again.";

/* ---- lazy firebase module (set when successfully imported) ---- */
let firebase = null;
let firebaseAuth = null;
let authModule = null;

async function loadFirebase() {
  if (firebase) return firebase;
  const [appMod, authMod] = await Promise.all([
    import("https://www.gstatic.com/firebasejs/13.4.0/firebase-app.js"),
    import("https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js"),
  ]);
  authModule = authMod;
  const app = appMod.initializeApp(firebaseConfig);
  const auth = authMod.getAuth(app);
  firebase = { app, auth };
  firebaseAuth = auth;
  return firebase;
}

/* ---- build the modal + account menu once (always runs) ---- */
const overlay = document.createElement("div");
overlay.className = "auth-overlay";
overlay.setAttribute("role", "dialog");
overlay.setAttribute("aria-modal", "true");
overlay.setAttribute("aria-label", "Account access");
overlay.innerHTML = `
  <div class="auth-modal">
    <button class="auth-close" type="button" aria-label="Close">&times;</button>
    <div class="auth-head">
      <span class="brand-mark" aria-hidden="true">MF</span>
      <div>
        <h2 data-auth-title>Sign in</h2>
        <p data-auth-sub>Access your MForce account.</p>
      </div>
    </div>
    <div class="auth-tabs" data-auth-tabs>
      <button type="button" data-tab="signin" class="active">Sign in</button>
      <button type="button" data-tab="signup">Create account</button>
    </div>
    <button class="auth-google" type="button" data-google>
      <svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59A14.4 14.4 0 0 1 9.75 24c0-1.6.27-3.14.76-4.59l-7.98-6.19A23.9 23.9 0 0 0 0 24c0 3.87.93 7.53 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.9-5.8l-7.73-6c-2.15 1.45-4.92 2.3-8.17 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
      Continue with Google
    </button>
    <div class="auth-divider"><span>or</span></div>
    <form data-auth-form novalidate>
      <div class="auth-field" data-name-field hidden>
        <label for="auth-name">Name</label>
        <input id="auth-name" type="text" autocomplete="name" placeholder="Ada Lovelace">
      </div>
      <div class="auth-field">
        <label for="auth-email">Email</label>
        <input id="auth-email" type="email" autocomplete="email" placeholder="you@example.com" required>
      </div>
      <div class="auth-field" data-password-field>
        <label for="auth-password">Password</label>
        <input id="auth-password" type="password" autocomplete="current-password" placeholder="••••••••" required>
      </div>
      <button class="auth-submit" type="submit" data-auth-submit>Sign in</button>
    </form>
    <button class="auth-link" type="button" data-reset>Forgot password?</button>
    <div class="auth-divider"><span>or</span></div>
    <button class="auth-link auth-phone-toggle" type="button" data-phone-toggle>Sign in with phone</button>
    <div class="auth-phone-panel" data-phone-panel hidden>
      <div class="auth-field auth-phone-row" style="margin-top:14px">
        <input id="auth-phone" type="tel" autocomplete="tel" placeholder="+1 555 000 0000" aria-label="Phone number">
        <button class="auth-submit" type="button" data-phone-send>Send code</button>
      </div>
      <div class="auth-field auth-phone-code" data-phone-code hidden>
        <label for="auth-code">Verification code</label>
        <input id="auth-code" type="text" inputmode="numeric" autocomplete="one-time-code" placeholder="123456">
        <button class="auth-submit" type="button" data-phone-confirm style="margin-top:10px">Verify &amp; sign in</button>
      </div>
      <div id="recaptcha-container"></div>
    </div>
    <p class="auth-error" data-auth-error role="alert"></p>
  </div>`;
document.body.appendChild(overlay);

const menu = document.createElement("div");
menu.className = "acct-menu";
menu.innerHTML = `
  <div class="acct-menu-head"><strong data-menu-name></strong><span data-menu-email></span></div>
  <button type="button" data-signout class="danger">Sign out</button>`;
document.body.appendChild(menu);

/* ---- element refs ---- */
const $ = (sel) => overlay.querySelector(sel);
const titleEl = $("[data-auth-title]");
const subEl = $("[data-auth-sub]");
const tabsEl = $("[data-auth-tabs]");
const form = $("[data-auth-form]");
const nameField = $("[data-name-field]");
const nameInput = $("#auth-name");
const emailInput = $("#auth-email");
const passwordField = $("[data-password-field]");
const passwordInput = $("#auth-password");
const submitBtn = $("[data-auth-submit]");
const resetBtn = $("[data-reset]");
const errorEl = $("[data-auth-error]");
const phonePanel = $("[data-phone-panel]");
const phoneCode = $("[data-phone-code]");
const phoneInput = $("#auth-phone");
const codeInput = $("#auth-code");

let mode = "signin"; // signin | signup | reset
let recaptchaVerifier = null;
let confirmationResult = null;

function showError(error) {
  errorEl.textContent = messageFor(error);
  errorEl.classList.add("show");
}
function clearError() {
  errorEl.textContent = "";
  errorEl.classList.remove("show");
}

function render() {
  clearError();
  const isSignup = mode === "signup";
  const isReset = mode === "reset";
  titleEl.textContent = isReset ? "Reset password" : isSignup ? "Create account" : "Sign in";
  subEl.textContent = isReset
    ? "We'll email you a reset link."
    : isSignup
    ? "Start using MForce today."
    : "Access your MForce account.";
  tabsEl.style.display = isReset ? "none" : "flex";
  tabsEl.querySelectorAll("button").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === (isSignup ? "signup" : "signin")));
  nameField.hidden = !isSignup;
  nameInput.required = isSignup;
  passwordField.hidden = isReset;
  passwordInput.required = !isReset;
  passwordInput.autocomplete = isSignup ? "new-password" : "current-password";
  submitBtn.textContent = isReset ? "Send reset link" : isSignup ? "Create account" : "Sign in";
  resetBtn.textContent = isReset ? "Back to sign in" : "Forgot password?";
}

function openModal() {
  menu.classList.remove("open");
  render();
  overlay.classList.add("open");
  document.body.style.overflow = "hidden";
  setTimeout(() => emailInput.focus(), 60);
}
// Expose for site.js (which owns the button click handler)
window.openAuthModal = openModal;
window.toggleMenu = toggleMenu;
function closeModal() {
  overlay.classList.remove("open");
  document.body.style.overflow = "";
  clearError();
}

overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeModal();
});
$(".auth-close").addEventListener("click", closeModal);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") { closeModal(); menu.classList.remove("open"); }
});

tabsEl.querySelectorAll("button").forEach((b) =>
  b.addEventListener("click", () => { mode = b.dataset.tab; render(); }));

resetBtn.addEventListener("click", () => {
  mode = mode === "reset" ? "signin" : "reset";
  render();
});

$("[data-phone-toggle]").addEventListener("click", () => {
  phonePanel.hidden = !phonePanel.hidden;
  if (!phonePanel.hidden) phoneInput.focus();
});

/* ---- Google ---- */
$("[data-google]").addEventListener("click", async () => {
  clearError();
  submitBtn.disabled = true;
  try {
    const f = await loadFirebase();
    await authModule.signInWithPopup(f.auth, new authModule.GoogleAuthProvider());
    closeModal();
  } catch (error) {
    showError(error);
  } finally {
    submitBtn.disabled = false;
  }
});

/* ---- email / password ---- */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  const email = emailInput.value.trim();
  const password = passwordInput.value;
  submitBtn.disabled = true;
  try {
    await loadFirebase();
    const authMod = await import("https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js");
    if (mode === "reset") {
      await authMod.sendPasswordReset(firebaseAuth, email);
      closeModal();
      return;
    }
    if (mode === "signup") {
      const name = nameInput.value.trim();
      const cred = await authMod.createUserWithEmailAndPassword(firebaseAuth, email, password);
      if (name) await authMod.updateProfile(cred.user, { displayName: name });
      await authMod.sendEmailVerification(cred.user).catch(() => {});
    } else {
      await authMod.signInWithEmailAndPassword(firebaseAuth, email, password);
    }
    closeModal();
  } catch (error) {
    showError(error);
  } finally {
    submitBtn.disabled = false;
  }
});

/* ---- phone ---- */
$("[data-phone-send]").addEventListener("click", async () => {
  clearError();
  const phone = phoneInput.value.trim();
  if (!phone) return showError({ message: "Enter your phone number with country code." });
  const sendBtn = $("[data-phone-send]");
  sendBtn.disabled = true;
  try {
    await loadFirebase();
    const authMod = await import("https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js");
    if (!recaptchaVerifier) {
      recaptchaVerifier = new authMod.RecaptchaVerifier(firebaseAuth, "recaptcha-container", { size: "normal" });
    }
    confirmationResult = await authMod.signInWithPhoneNumber(firebaseAuth, phone, recaptchaVerifier);
    phoneCode.hidden = false;
    codeInput.focus();
  } catch (error) {
    if (recaptchaVerifier) { recaptchaVerifier.clear(); recaptchaVerifier = null; }
    showError(error);
  } finally {
    sendBtn.disabled = false;
  }
});

$("[data-phone-confirm]").addEventListener("click", async () => {
  clearError();
  if (!confirmationResult) return showError({ message: "Request a code first." });
  const code = codeInput.value.trim();
  try {
    await confirmationResult.confirm(code);
    closeModal();
  } catch (error) {
    showError(error);
  }
});

/* ---- account menu ---- */
function toggleMenu(anchor) {
  const open = menu.classList.toggle("open");
  if (open) {
    const rect = anchor.getBoundingClientRect();
    menu.style.top = `${rect.bottom + 8}px`;
    menu.style.right = `${Math.max(16, window.innerWidth - rect.right)}px`;
  }
}
document.addEventListener("click", (e) => {
  if (!menu.contains(e.target) && !e.target.closest("[data-auth-toggle]")) {
    menu.classList.remove("open");
  }
});
$("[data-signout]").addEventListener("click", async () => {
  try {
    await loadFirebase();
    const authMod = await import("https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js");
    await authMod.signOut(firebaseAuth).catch(() => {});
  } catch (_) { /* ignore */ }
  menu.classList.remove("open");
});

/* ---- auth state → account button ---- */
function initials(name) {
  const parts = (name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "•";
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

// Expose a lightweight auth shim so site.js can read currentUser without Firebase
window.auth = {
  get currentUser() { return null; },
};
// If Firebase loads successfully, wire up the real observer.
loadFirebase().then((f) => {
  const authMod = import("https://www.gstatic.com/firebasejs/13.4.0/firebase-auth.js");
  authMod.then((m) => {
    m.onAuthStateChanged(f.auth, (user) => {
      document.querySelectorAll("[data-auth-toggle]").forEach((btn) => {
        if (user) {
          const name = user.displayName || user.email || user.phoneNumber || "Account";
          btn.innerHTML = `<span class="acct-avatar" aria-hidden="true"></span><span class="acct-name"></span><span class="acct-caret" aria-hidden="true">&#9662;</span>`;
          btn.querySelector(".acct-avatar").textContent = initials(user.displayName || user.email);
          btn.querySelector(".acct-name").textContent = String(name).split(" ")[0];
          btn.setAttribute("aria-label", "Account menu");
        } else {
          btn.textContent = "Sign in";
          btn.setAttribute("aria-label", "Sign in");
        }
      });
      if (user) {
        const nameEl = $("[data-menu-name]");
        const emailEl = $("[data-menu-email]");
        if (nameEl) nameEl.textContent = user.displayName || "Your account";
        if (emailEl) emailEl.textContent = user.email || user.phoneNumber || "";
      }
    });
  });
}).catch(() => {
  /* Firebase unavailable; UI still works via window.openAuthModal fallback */
});
