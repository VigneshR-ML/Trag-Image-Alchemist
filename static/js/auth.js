import {
    loginWithGoogle,
    handleRedirectResult,
    logoutUser,
    initAuthStateObserver
  } from "./firebase-config.js";
  
  document.addEventListener("DOMContentLoaded", async () => {
    // Button references (note footer IDs too)
    const loginBtns = [
      document.getElementById("login-btn"),
      document.getElementById("login-btn-footer"),
    ].filter(Boolean);
    const signupBtns = [
      document.getElementById("signup-btn"),
      document.getElementById("signup-btn-footer"),
    ].filter(Boolean);
    const logoutBtn = document.getElementById("logout-btn");
    const userDisplay = document.getElementById("user-display");
  
    // Finalize redirect if we came back from Google
    const { user, error } = await handleRedirectResult();
    if (error) showAlert(error, "danger");
    else if (user) showAlert("Successfully signed in!", "success");
  
    // Show/hide UI based on auth state
    initAuthStateObserver((u) => {
      const signedIn = !!u;
      loginBtns.forEach(btn => (btn.style.display = signedIn ? "none" : "inline-block"));
      signupBtns.forEach(btn => (btn.style.display = signedIn ? "none" : "inline-block"));
      if (logoutBtn) logoutBtn.style.display = signedIn ? "inline-block" : "none";
      if (userDisplay) {
        userDisplay.style.display = signedIn ? "block" : "none";
        if (u) userDisplay.textContent = u.email;
      }
    });
  
    // Attach the same handler to all sign-in/up buttons
    const handleGoogleAuth = () => {
      loginWithGoogle();
      // no .catch here — if redirect fails, it'll fall into your global error handling
    };
    loginBtns.forEach(btn => btn.addEventListener("click", handleGoogleAuth));
    signupBtns.forEach(btn => btn.addEventListener("click", handleGoogleAuth));
  
    // Logout
    if (logoutBtn) {
      logoutBtn.addEventListener("click", async () => {
        showLoading("Logging out…");
        const { error } = await logoutUser();
        hideLoading();
        if (error) showAlert(error, "danger");
        else showAlert("Successfully logged out!", "success");
      });
    }
  });
  