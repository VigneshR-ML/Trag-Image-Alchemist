import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithRedirect,
  getRedirectResult,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyCTnxUqajXfvKkFLrOV7rL6RqlNX3jNz_k",
    authDomain: "trag-image-alchemist.firebaseapp.com",
    projectId: "trag-image-alchemist",
    storageBucket: "trag-image-alchemist.firebasestorage.app",
    messagingSenderId: "74227540925",
    appId: "1:74227540925:web:57400a523702ee15e428d4",
    measurementId: "G-M1H0JFZ4JB"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

export const provider = new GoogleAuthProvider();
// always show account chooser
provider.setCustomParameters({ prompt: "select_account" });

export const loginWithGoogle = () => {
  // don’t await past the redirect – Firebase will navigate the browser
  showLoading("Redirecting to Google Sign-In…");
  signInWithRedirect(auth, provider);
};

export const handleRedirectResult = async () => {
  try {
    const result = await getRedirectResult(auth);
    if (result) {
      return { user: result.user, error: null };
    }
    return { user: null, error: null };
  } catch (e) {
    return { user: null, error: e.message };
  } finally {
    hideLoading();
  }
};

export const logoutUser = async () => {
  try {
    await auth.signOut();
    return { error: null };
  } catch (e) {
    return { error: e.message };
  }
};

export const initAuthStateObserver = (cb) =>
  onAuthStateChanged(auth, cb);
