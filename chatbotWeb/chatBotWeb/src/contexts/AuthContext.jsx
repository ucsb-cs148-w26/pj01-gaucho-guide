import React, { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  updateProfile,
} from "firebase/auth";
import { auth, hasConfig } from "../lib/firebase";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

const toUserView = (u) => {
  if (!u) return null;
  return {
    email: u.email,
    name: u.displayName || u.email?.split("@")[ 0] || "UCSB Student",
    picture:
      u.photoURL ||
      `https://ui-avatars.com/api/?name=${encodeURIComponent(
        u.displayName || "UCSB Student"
      )}&background=003660&color=febc11&size=120`,
    verified: u.emailVerified,
  };
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!hasConfig || !auth) {
      setLoading(false);
      return;
    }

    const unsub = onAuthStateChanged(auth, (u) => {
      setFirebaseUser(u);
      setUser(toUserView(u));
      setLoading(false);
    });

    return () => unsub();
  }, []);

  const ensureUcsb = (email) => {
    const normalized = (email || "").trim().toLowerCase();
    if (!normalized.endsWith("@ucsb.edu")) {
      throw new Error("Only @ucsb.edu email addresses are allowed.");
    }
    return normalized;
  };

  const signUpWithEmail = async (email, password, displayName) => {
    if (!auth) throw new Error("Firebase is not configured.");
    const safeEmail = ensureUcsb(email);
    const cred = await createUserWithEmailAndPassword(auth, safeEmail, password);
    if (displayName?.trim()) {
      await updateProfile(cred.user, { displayName: displayName.trim() });
      setUser(toUserView({ ...cred.user, displayName: displayName.trim() }));
    }
    return cred.user;
  };

  const signInWithEmail = async (email, password) => {
    if (!auth) throw new Error("Firebase is not configured.");
    const safeEmail = ensureUcsb(email);
    const cred = await signInWithEmailAndPassword(auth, safeEmail, password);
    return cred.user;
  };

  const signInWithGoogle = async () => {
  if (!auth) throw new Error("Firebase is not configured.");

  const provider = new GoogleAuthProvider();

  provider.setCustomParameters({
    hd: "ucsb.edu"
  });

  const result = await signInWithPopup(auth, provider);

  const email = result.user.email || "";

  if (!email.endsWith("@ucsb.edu")) {
    await firebaseSignOut(auth);
    throw new Error("Only @ucsb.edu accounts allowed.");
  }

  return result.user;
};

  const signOut = async () => {
    if (!auth) return;
    await firebaseSignOut(auth);
    setFirebaseUser(null);
    setUser(null);
  };

  const getIdToken = async () => {
    if (!firebaseUser) return null;
    return firebaseUser.getIdToken();
  };

  const value = {
    user,
    firebaseUser,
    loading,
    signOut,
    signInWithGoogle,
    getIdToken,
    isAuthenticated: !!user,
    authEnabled: hasConfig,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
