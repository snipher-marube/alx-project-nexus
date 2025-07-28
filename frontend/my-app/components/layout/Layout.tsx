import React, { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import LoginModal from "@/components/common/LoginModal";
import SignupModal from "@/components/common/SignupModal";
import Footer from "@/components/layout/Footer";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const storedId = localStorage.getItem("userId");
    if (storedId) {
      setUserId(storedId);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = (id: string) => {
    localStorage.setItem("userId", id);
    setUserId(id);
    setIsLoggedIn(true);
    setShowLogin(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("userId");
    setUserId(null);
    setIsLoggedIn(false);
  };

  const openLogin = () => {
    setShowLogin(true);
    setShowSignup(false);
  };

  const openSignup = () => {
    setShowSignup(true);
    setShowLogin(false);
  };

  return (
    <>
      <Header
        onShowLogin={openLogin}
        onShowSignup={openSignup}
        isLoggedIn={isLoggedIn}
        onLogout={handleLogout}
      />

      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onSwitch={openSignup}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {showSignup && (
        <SignupModal
          onClose={() => setShowSignup(false)}
          onSwitch={openLogin}
        />
      )}

      <main>{children}</main>
      <Footer />
    </>
  );
}
