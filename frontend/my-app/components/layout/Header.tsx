import React from "react";

interface HeaderProps {
  onShowLogin: () => void;
  onShowSignup: () => void;
}
const Header: React.FC<HeaderProps> = ({ onShowLogin, onShowSignup }) => {
  return (
    <header className="bg-gray-800 p-4 shadow-md  ">
      <h1 className="text-red-300 text-4xl text-center">E-Commerce App</h1>
      <div className="absolute start-0 top-0 size-140">
        <button className=" ml-4 bg-blue-600 text-white p-2 rounded hover:bg-red-700" onClick={onShowLogin}>
          Login</button>
        <button className=" ml-2 bg-green-600 text-white p-2 rounded hover:bg-red-700" onClick={onShowSignup}>
          Sign Up  </button>`
      </div>
      <nav className="mt-4 justify-items-center m1-4 p1-3 text-2xl">
        <ul className="flex space-x-5">
          <li>
            <a href="/frontend/my-app/pages/index.tsx" className="text-gray-50  hover:text-red-400">Home</a>
          </li>
          <li>
            <a href="/products" className="text-white hover:text-red-400">Products</a>
          </li>
          <li>
            <a href="/cart" className="text-white hover:text-red-400">Cart</a>
          </li>
          <li>
            <a href="/profile" className="text-white hover:text-red-400">Profile</a>
          </li>
        </ul>
      </nav>
    </header>
  );
}
export default Header;