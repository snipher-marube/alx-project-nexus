import React from 'react';

interface SignupModalProps {
  onClose: () => void;
  onSwitch: () => void;
}

export default function SignupModal({ onClose, onSwitch }: SignupModalProps) {
  return (
    <div className="text-black fixed inset-0 bg-transparent flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative">
        <h2 className="text-2xl font-bold mb-4 text-center">Sign Up</h2>
        <form className='text-black'>
          <input type="text" placeholder="First-Name" className="w-full p-2 mb-4 border rounded" />
          <input type="text" placeholder="Last-Name" className="w-full p-2 mb-4 border rounded" />
          <input type="email" placeholder="Email" className="w-full p-2 mb-4 border rounded" />
          <input type="number" placeholder="Phone number" className="w-full p-2 mb-4 border rounded" />
          <input type="password" placeholder="Password" className="w-full p-2 mb-4 border rounded" />
          <input type="password" placeholder="Re-enter Password" className="w-full p-2 mb-4 border rounded" />
          <button className="w-full bg-green-600 text-black p-2 rounded hover:bg-green-700">
            Sign Up
          </button>
        </form>
        <p className="mt-4 text-center">
          Already have an account?{' '}
          <button onClick={onSwitch} className="text-green-600 hover:underline">Login</button>
        </p>
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 text-gray-600 hover:text-black text-xl font-bold"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
