import React, { useState } from "react";
import Link from "next/link";
import { useCart } from "@/context/CartContext";

interface HeaderProps {
  onShowLogin: () => void;
  onShowSignup: () => void;
}

const Header: React.FC<HeaderProps> = ({ onShowLogin, onShowSignup }) => {
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const { cartItems } = useCart();

  const toggleAccountMenu = () => {
    setShowAccountMenu((prev) => !prev);
  };

  return (
    <header className="bg-gray-800 p-4 shadow-md relative">
      <h1 className="text-red-300 text-4xl text-center">E-Commerce App</h1>

      <nav className="mt-4 flex justify-center">
        <ul className="flex space-x-6 text-2xl items-center relative">
          <li>
            <Link href="/" className="text-gray-50 hover:text-red-400">
              Home
            </Link>
          </li>
          <li>
            <Link href="/products" className="text-white hover:text-red-400">
              Products
            </Link>
          </li>
          <li>
            <Link href="/Cart" className="text-white hover:text-red-400">
              Cart

            </Link>
          </li>
          
          <li className="relative">
            <button 
              className="text-white hover:text-red-400 focus:outline-none"
              onClick={toggleAccountMenu}
              aria-expanded={showAccountMenu}
            >
              Account {'↓'}
            </button>
            {showAccountMenu && (
              <div className="absolute right-0 mt-2 w-40 justify-items-center text-black bg-white border rounded shadow z-10">
                <button
                  className="justify-text-center block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                  onClick={onShowLogin}
                >
                    Login
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                  onClick={onShowSignup}
                >
                  Sign Up
                </button>
                <li>
            <Link href="/orders" className="text-black text-sm">
                Orders
            </Link>
          </li>
              </div>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
