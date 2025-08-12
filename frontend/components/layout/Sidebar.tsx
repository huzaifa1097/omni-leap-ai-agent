'use client';

import React, { useState } from 'react';
import { Bot, UserCircle, Power, Sun, Moon, MessageSquare, LayoutDashboard, PlusCircle } from 'lucide-react';
import { signOut } from 'firebase/auth';
import { auth } from '../../lib/firebase';
import Image from 'next/image';

type Page = 'chat' | 'profile' | 'dashboard';

interface SidebarProps {
  currentPage: Page;
  setCurrentPage: (page: Page) => void;
  isDark: boolean;
  setIsDark: (isDark: boolean) => void;
  startNewChat: () => void;
}

// A simple, reusable Modal component
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
            Yes, Logout
          </button>
        </div>
      </div>
    </div>
  );
};

// A new component for the sidebar buttons with tooltips
const SidebarButton = ({ icon, text, onClick, isActive = false }: { icon: React.ReactNode, text: string, onClick: () => void, isActive?: boolean }) => (
    <div className="relative group flex justify-center">
        <button 
          onClick={onClick} 
          className={`p-3 rounded-lg transition-all duration-300 w-full ${isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}
        >
          <div className="icon-animate">{icon}</div>
        </button>
        <div className="tooltip absolute left-full ml-4 px-3 py-2 text-sm font-semibold text-white bg-gray-900 rounded-md shadow-lg whitespace-nowrap">
            {text}
        </div>
    </div>
);


export const Sidebar = ({ currentPage, setCurrentPage, isDark, setIsDark, startNewChat }: SidebarProps) => {
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      setShowLogoutConfirm(false);
    } catch (error) {
      console.error("Error signing out: ", error);
    }
  };

  return (
    <>
      <nav className="w-20 bg-gray-800 p-3 flex flex-col items-center justify-between transition-all duration-300 hover:w-24">
        <div className="w-full space-y-4">
          <div className="flex justify-center p-2 mb-4">
            <Image src="/omni-leap-logo.svg" alt="OmniLeap Logo" width={40} height={40} />
          </div>
          <SidebarButton 
            icon={<PlusCircle size={24} className="mx-auto" />}
            text="New Chat"
            onClick={startNewChat}
          />
          <SidebarButton 
            icon={<MessageSquare size={24} className="mx-auto" />}
            text="Chat"
            onClick={() => setCurrentPage('chat')}
            isActive={currentPage === 'chat'}
          />
          <SidebarButton 
            icon={<LayoutDashboard size={24} className="mx-auto" />}
            text="Dashboard"
            onClick={() => setCurrentPage('dashboard')}
            isActive={currentPage === 'dashboard'}
          />
          <SidebarButton 
            icon={<UserCircle size={24} className="mx-auto" />}
            text="Profile"
            onClick={() => setCurrentPage('profile')}
            isActive={currentPage === 'profile'}
          />
        </div>
        <div className="w-full space-y-4">
          <SidebarButton 
            icon={isDark ? <Sun size={24} className="mx-auto" /> : <Moon size={24} className="mx-auto" />}
            text={isDark ? "Light Mode" : "Dark Mode"}
            onClick={() => setIsDark(!isDark)}
          />
          <SidebarButton 
            icon={<Power size={24} className="mx-auto" />}
            text="Logout"
            onClick={() => setShowLogoutConfirm(true)}
          />
        </div>
      </nav>

      <ConfirmationModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={handleLogout}
        title="Confirm Logout"
      >
        Are you sure you want to log out of your OmniLeap account?
      </ConfirmationModal>
    </>
  );
};
