import React from "react";

interface HeaderProps {
  onShowLogin: () => void;
  onShowSignup: () => void;
}
const Header: React.FC<HeaderProps> = ({ onShowLogin, onShowSignup }) => {
  return (
    <header className="bg-gray-800 p-4 shadow-md  ">
      <h1 className="text-red-300 text-xl text-center">E-Commerce App</h1>
      <div className="absolute start-0 top-0 size-140">
        <button className=" ml-4 bg-blue-600 text-white p-2 rounded hover:bg-red-700" onClick={onShowLogin}>
          Login</button>
        <button className=" ml-2 bg-green-600 text-white p-2 rounded hover:bg-red-700" onClick={onShowSignup}>
          Sign Up  </button>`
      </div>
    </header>
  );
}
export default Header;