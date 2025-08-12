'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { AuthProvider, useAuth } from '../lib/auth';
import { LoginPage } from '../components/auth/LoginPage';
import { ProfilePage } from '../components/user/ProfilePage';
import { Sidebar } from '../components/layout/Sidebar';
import { LoaderCircle } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import { DashboardPage, HistoryMessage } from '../components/user/DashboardPage';

// --- TYPES ---
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
}

// --- DYNAMIC IMPORT FOR CHAT PAGE (Client-side only) ---
const ChatPage = dynamic(
  () => import('../components/chat/ChatPage').then(mod => mod.ChatPage), 
  {
    ssr: false,
    loading: () => <div className="flex items-center justify-center h-full"><LoaderCircle className="animate-spin" size={32} /></div>
  }
);

type Page = 'chat' | 'profile' | 'dashboard';

const AppRouter = () => {
  const { user } = useAuth();
  
  // --- STATE MANAGEMENT ---
  const [currentPage, setCurrentPage] = useState<Page>('chat');
  const [isDark, setIsDark] = useState(true);
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);

  const startNewChat = () => {
    setSessionId(uuidv4());
    setMessages([{ id: uuidv4(), text: `Hi ${user?.displayName || 'there'}! I'm ready for a new conversation.`, sender: 'agent' }]);
    setCurrentPage('chat'); // Ensure the user is on the chat page
  };

  // --- NEW FUNCTION TO LOAD A PAST CONVERSATION ---
  const loadConversation = (historyMessages: HistoryMessage[]) => {
    // Convert the history format to the chat format
    const loadedMessages = historyMessages.map(msg => ({
        id: uuidv4(), // Generate new IDs for React keys
        text: msg.text,
        sender: msg.sender,
    }));
    setMessages(loadedMessages);
    // Set the session ID from the loaded conversation
    setSessionId(historyMessages[0]?.session_id || uuidv4());
    // Switch the user to the chat page to see the conversation
    setCurrentPage('chat');
  };

  useEffect(() => {
    if (user && messages.length === 0) {
      startNewChat();
    }
  }, [user]);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div className="flex h-screen">
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage} 
        isDark={isDark} 
        setIsDark={setIsDark}
        startNewChat={startNewChat}
      />
      <main className="flex-1 bg-gray-100 text-black dark:bg-gray-900 dark:text-white transition-colors duration-300">
        {currentPage === 'chat' && (
          <ChatPage 
            sessionId={sessionId}
            messages={messages}
            setMessages={setMessages}
          />
        )}
        {currentPage === 'profile' && <ProfilePage />}
        {currentPage === 'dashboard' && <DashboardPage loadConversation={loadConversation} />} 
      </main>
    </div>
  );
};

// --- ROOT COMPONENT ---
export default function Home() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
