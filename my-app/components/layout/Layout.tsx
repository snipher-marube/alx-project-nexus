import React, { useState } from "react";
import Header from "@/components/layout/Header";
import LoginModal from "@/components/common/LoginModal";
import SignupModal from "@/components/common/SignupModal";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  // Functions to open modals, passed down to Header
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
      <Header onShowLogin={openLogin} onShowSignup={openSignup} />

      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onSwitch={() => {
            setShowLogin(false);
            setShowSignup(true);
          }}
        />
      )}

      {showSignup && (
        <SignupModal
          onClose={() => setShowSignup(false)}
          onSwitch={() => {
            setShowSignup(false);
            setShowLogin(true);
          }}
        />
      )}

      <main>{children}</main>
    </>
  );
}
