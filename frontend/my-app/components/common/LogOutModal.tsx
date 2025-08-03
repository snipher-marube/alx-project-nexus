import React from 'react';
import axios from 'axios';

export default function LogoutButton() {
  const handleLogout = async () => {
    const token = localStorage.getItem('token');

    if (!token) {
      alert('You are not logged in.');
      return;
    }

    try {
      await axios.post(
        'https://alx-project-nexus-psi.vercel.app/api/v1/auth/auth_logout_create',
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      localStorage.removeItem('token');
      alert('Logged out successfully!');
      window.location.reload(); 

    } catch (error: any) {
      console.error('Logout failed:', error);
      alert('Failed to log out.');
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
    >
      Logout
    </button>
  );
}
