import React, { useState } from 'react';
import axios from 'axios';

interface LoginModalProps {
  onClose: () => void;
  onSwitch: () => void;
}

export default function LoginModal({ onClose, onSwitch }: LoginModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await axios.post('https://alx-project-nexus-psi.vercel.app/auth/login', {
        email,
        password
      });

      // You might want to store token or user info from res.data
      console.log("Login success:", res.data);

      onClose(); // close modal on success
    } catch (err: any) {
      const message = err.response?.data?.message || 'Login failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-transparent flex justify-center items-center z-50 text-black">
      <div className="relative bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-center">Login</h2>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            className="text-black w-full p-2 mb-4 border rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-2 mb-4 border rounded text-black"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className={`w-full p-2 rounded ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
          >
            {loading ? 'Logging in...' : 'Login'}
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
