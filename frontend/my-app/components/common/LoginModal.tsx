import React from 'react';

interface LoginModalProps {
  onClose: () => void;
  onSwitch: () => void;
}

export default function LoginModal({ onClose, onSwitch }: LoginModalProps) {
  return (
    <div className="fixed inset-0 bg-transparent flex justify-center items-center z-50 text-black">
      <div className="relative bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-center">Login</h2>
        <form>
          <input
            type="email"
            placeholder="Email"
            className="text-black w-full p-2 mb-4 border rounded"
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-2 mb-4 border rounded text-black"
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-black p-2 rounded hover:bg-blue-700"
          >
            Login
          </button>
        </form>
        <p className="mt-4 text-center">
          Don’t have an account?{' '}
          <button
            type="button"
            onClick={onSwitch}
            className="text-blue-600 hover:underline"
          >
            Sign up
          </button>
        </p>
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-black hover:text-black text-xl font-bold"
          aria-label="Close login modal"
          type="button"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
