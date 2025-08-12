'use client';

import React, { useState } from 'react';
import { useAuth } from '../../lib/auth';
import { deleteUser } from 'firebase/auth';
import { Trash2 } from 'lucide-react';

// A reusable Modal component for confirmations
const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, children }: any) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-sm mx-4">
        <h3 className="text-lg font-bold text-white mb-4">{title}</h3>
        <div className="text-gray-300 mb-6">{children}</div>
        <div className="flex justify-end gap-4">
          <button 
            onClick={onClose} 
            className="px-4 py-2 rounded-md bg-gray-600 hover:bg-gray-500 text-white font-semibold transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm} 
            className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-500 text-white font-semibold transition-colors"
          >
            Yes, Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export const ProfilePage = () => {
    const { user } = useAuth();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [error, setError] = useState('');

    const handleDeleteAccount = async () => {
        if (!user) return;
        try {
            await deleteUser(user);
            // The onAuthStateChanged listener in our AuthProvider will handle the redirect.
        } catch (error: any) {
            console.error("Error deleting account:", error);
            setError("Failed to delete account. You may need to log out and log back in before trying again.");
        }
        setShowDeleteConfirm(false);
    };

    if (!user) {
        return <div className="p-8 text-white">Loading user data...</div>;
    }

    // Get the account creation date
    const creationDate = user.metadata.creationTime 
        ? new Date(user.metadata.creationTime).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric'
          }) 
        : 'Not available';

    return (
        <>
            <div className="p-4 md:p-8 text-white h-full overflow-y-auto">
                <div className="max-w-2xl mx-auto">
                    <h1 className="text-3xl font-bold mb-8">My Profile</h1>
                    
                    <div className="bg-gray-800 p-6 rounded-lg flex items-center gap-6">
                        <img 
                            src={user.photoURL || `https://api.dicebear.com/8.x/initials/svg?seed=${user.email}`} 
                            alt="Profile" 
                            className="w-24 h-24 rounded-full border-4 border-blue-500"
                        />
                        <div className="space-y-2">
                            <h2 className="text-2xl font-bold">{user.displayName || 'Anonymous User'}</h2>
                            <p className="text-gray-400">{user.email}</p>
                            <p className="text-xs text-gray-500">Member since: {creationDate}</p>
                        </div>
                    </div>

                    <div className="mt-12">
                        <h3 className="text-xl font-semibold text-red-400 mb-4">Danger Zone</h3>
                        <div className="bg-gray-800 p-6 rounded-lg flex justify-between items-center">
                            <div>
                                <h4 className="font-bold">Delete Account</h4>
                                <p className="text-sm text-gray-400 mt-1">Permanently delete your account and all of your data. This action cannot be undone.</p>
                            </div>
                            <button 
                                onClick={() => setShowDeleteConfirm(true)}
                                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-red-300 bg-red-900/50 rounded-lg hover:bg-red-800/50 transition-colors"
                            >
                                <Trash2 size={16} />
                                Delete
                            </button>
                        </div>
                        {error && <p className="text-red-400 text-sm mt-4">{error}</p>}
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleDeleteAccount}
                title="Delete Your Account"
            >
                Are you absolutely sure you want to delete your account? All of your data, including conversation history, will be permanently erased. This action cannot be undone.
            </ConfirmationModal>
        </>
    );
};
