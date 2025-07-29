/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState } from "react";
import { CiMenuBurger } from "react-icons/ci";
import Link from "next/link";
import { useCart } from "@/context/CartContext";

interface HeaderProps {
  onShowLogin: () => void;
  onShowSignup: () => void;
}

const Header: React.FC<HeaderProps> = ({ onShowLogin, onShowSignup }) => {
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [showHamburger, setShowHamburger] = useState(false);
  const { cartItems } = useCart();

  const toggleAccountMenu = () => {
    setShowAccountMenu((prev) => !prev);
  };

  const toggleMobileMenu = () => {
    setShowHamburger(() => !showHamburger);
  }

  return (
    <header className="bg-gray-800 py-4 px-5 md:px-8 shadow-md relative flex items-center justify-between">
      <h1 className="text-red-300 text-4xl text-center">E-Commerce App</h1>

      <nav className="hidden md:block mt-4 flex justify-center">
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
              <div className="absolute right-[-30px] mt-2 pb-4 w-40 text-black bg-white border border-gray-300 rounded shadow z-10">
                <button
                  className=" block w-full text-left px-4 py-2 text-md hover:bg-gray-100"
                  onClick={onShowLogin}
                >
                    Login
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-md hover:bg-gray-100"
                  onClick={onShowSignup}
                >
                  Sign Up
                </button>
      
                <Link href="/orders" className="text-black text-md p-4">
                    Orders
                </Link>
              </div>
            )}
          </li>
        </ul>
      </nav>
      
      {/* mobile navigation */}
      <CiMenuBurger className="md:hidden text-5xl" onClick={toggleMobileMenu} />
			{showHamburger && (
      <nav className="md:hidden mt-4 absolute top-[65px] right-0 p-5 w-full bg-white z-50 border border-gray-400 shadow-lg rounded-b-md">
        <ul className="flex flex-col gap-6 space-x-6 text-2xl items-center relative">
          <li>
            <Link href="/" className="text-black hover:text-red-400">
              Home
            </Link>
          </li>
          <li>
            <Link href="/products" className="text-black hover:text-red-400">
              Products
            </Link>
          </li>
          <li>
            <Link href="/Cart" className="text-black hover:text-red-400">
              Cart

            </Link>
          </li>
          
          <li className="relative">
            <button 
              className="text-black hover:text-red-400 focus:outline-none"
              onClick={toggleAccountMenu}
              aria-expanded={showAccountMenu}
            >
              Account {'↓'}
            </button>
            {showAccountMenu && (
              <div className=" mt-2 w-40 justify-center text-black bg-white">
                <button
                  className=" block w-full text-left px-4 py-2 text-md hover:bg-gray-100"
                  onClick={onShowLogin}
                >
                    Login
                </button>
                <button
                  className="block w-full text-left px-4 py-2 text-md hover:bg-gray-100"
                  onClick={onShowSignup}
                >
                  Sign Up
                </button>
                <Link href="/orders" className="text-black text-md px-4 py-4">
                    Orders
                </Link>
              </div>
            )}
          </li>
        </ul>
      </nav>)}
    </header>
  );
};

export default Header;
