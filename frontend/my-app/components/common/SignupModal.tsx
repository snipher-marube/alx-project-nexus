/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';

interface SignupModalProps {
  onClose: () => void;
  onSwitch: () => void;
}

export default function SignupModal({ onClose, onSwitch }: SignupModalProps) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('https://alx-project-nexus-psi.vercel.app/api/v1/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email,
          phone,
          user_type: 'CUSTOMER',
          password,
          password2: confirmPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || JSON.stringify(data));
      }

      alert("Account created successfully! Check your email for verification.");
      onClose();
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="text-black fixed inset-0 bg-transparent flex justify-center items-center z-50">
      <div className="bg-neutral-50 rounded-lg shadow-lg w-full max-w-md p-6 relative">
        <h2 className="text-2xl font-bold mb-4 text-center">Sign Up</h2>

        <form onSubmit={handleSubmit} className="text-black">
          <input
            type="text"
            placeholder="First Name"
            className="w-full p-2 mb-4 border rounded"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Last Name"
            className="w-full p-2 mb-4 border rounded"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email"
            className="w-full p-2 mb-4 border rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="tel"
            placeholder="Phone Number"
            className="w-full p-2 mb-4 border rounded"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full p-2 mb-4 border rounded"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Re-enter Password"
            className="w-full p-2 mb-4 border rounded"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className={`w-full p-2 rounded ${loading ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'} text-white`}
          >
            {loading ? 'Signing up...' : 'Sign Up'}
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
