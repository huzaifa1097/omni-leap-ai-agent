'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../lib/auth';
import { Bot, User, LoaderCircle, MessageSquare, Trash2 } from 'lucide-react';

// Define the shape of a single message from the backend
export interface HistoryMessage {
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  session_id: string;
}

// Define the shape of a conversation, grouped by session
interface Conversation {
  session_id: string;
  messages: HistoryMessage[];
  first_timestamp: string;
}

interface DashboardPageProps {
    loadConversation: (messages: HistoryMessage[]) => void;
}

// A simple, reusable Modal component for confirmations
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

export const DashboardPage = ({ loadConversation }: DashboardPageProps) => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
  
  // --- THIS IS THE FIX ---
  // The URL now correctly points to your local backend server for development.
  const BACKEND_URL = 'https://omni-leap-backend-service-280476321364.asia-south1.run.app';

  const fetchHistory = async () => {
    if (!user) return;
    try {
      setIsLoading(true);
      setError(null);
      const idToken = await user.getIdToken();
      
      const response = await fetch(`${BACKEND_URL}/api/v1/chat/history`, {
        headers: { 'Authorization': `Bearer ${idToken}` }
      });

      if (!response.ok) throw new Error('Failed to fetch chat history.');
      const data = await response.json();
      
      const groupedConversations: { [key: string]: Conversation } = {};
      (data.history || []).forEach((msg: HistoryMessage) => {
        if (!groupedConversations[msg.session_id]) {
          groupedConversations[msg.session_id] = { session_id: msg.session_id, messages: [], first_timestamp: msg.timestamp };
        }
        groupedConversations[msg.session_id].messages.push(msg);
      });
      
      const sortedConversations = Object.values(groupedConversations).sort((a, b) => 
        new Date(b.first_timestamp).getTime() - new Date(a.first_timestamp).getTime()
      );
      setConversations(sortedConversations);
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [user]);

  const handleDeleteAllHistory = async () => {
      if (!user) return;
      try {
        const idToken = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/v1/chat/history`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${idToken}` }
        });
        if (!response.ok) throw new Error('Failed to delete history.');
        
        // Refresh the conversation list after deletion
        fetchHistory();
        setShowDeleteAllConfirm(false);

      } catch (err: any) {
          setError(err.message || "An error occurred while deleting history.");
          setShowDeleteAllConfirm(false);
      }
  };

  const handleDeleteSingleHistory = async () => {
      if (!user || !sessionToDelete) return;
      try {
        const idToken = await user.getIdToken();
        const response = await fetch(`${BACKEND_URL}/api/v1/chat/history/${sessionToDelete}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${idToken}` }
        });
        if (!response.ok) throw new Error('Failed to delete session.');
        
        // Refresh the conversation list after deletion
        fetchHistory();
        setSessionToDelete(null); // Close the modal

      } catch (err: any) {
          setError(err.message || "An error occurred while deleting session.");
          setSessionToDelete(null); // Close the modal
      }
  };

  return (
    <>
      <div className="p-4 md:p-8 text-white h-full overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Conversation History</h1>
            {conversations.length > 0 && (
                <button 
                    onClick={() => setShowDeleteAllConfirm(true)}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-red-300 bg-red-900/50 rounded-lg hover:bg-red-800/50 transition-colors"
                >
                    <Trash2 size={16} />
                    Delete All History
                </button>
            )}
        </div>
        
        {isLoading && <div className="flex justify-center items-center h-48"><LoaderCircle className="animate-spin" size={32} /></div>}
        {error && <div className="bg-red-900 border border-red-600 text-red-200 px-4 py-3 rounded-lg"><p><strong>Error:</strong> {error}</p></div>}
        {!isLoading && !error && conversations.length === 0 && (
          <div className="text-center py-16">
            <MessageSquare size={48} className="mx-auto text-gray-500 mb-4" />
            <h2 className="text-xl font-semibold">No History Found</h2>
            <p className="text-gray-400 mt-2">Start a new conversation to see your history here.</p>
          </div>
        )}
        {!isLoading && !error && conversations.length > 0 && (
          <div className="space-y-4">
            {conversations.map(convo => (
              <div key={convo.session_id} className="group flex items-center justify-between bg-gray-800 p-4 rounded-lg hover:bg-gray-700 transition-colors">
                <button onClick={() => loadConversation(convo.messages)} className="flex-1 text-left mr-4">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2 truncate">{convo.messages[0]?.text || 'Empty Chat'}</h3>
                    <p className="text-xs text-gray-500">{convo.messages.length} messages - Started on {new Date(convo.first_timestamp).toLocaleDateString()}</p>
                </button>
                <button 
                    onClick={(e) => { e.stopPropagation(); setSessionToDelete(convo.session_id); }}
                    className="p-2 rounded-full text-gray-500 hover:bg-red-900/50 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete this conversation"
                >
                    <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      <ConfirmationModal isOpen={showDeleteAllConfirm} onClose={() => setShowDeleteAllConfirm(false)} onConfirm={handleDeleteAllHistory} title="Delete All History">
        Are you sure you want to permanently delete your entire conversation history? This action cannot be undone.
      </ConfirmationModal>
      <ConfirmationModal isOpen={!!sessionToDelete} onClose={() => setSessionToDelete(null)} onConfirm={handleDeleteSingleHistory} title="Delete Conversation">
        Are you sure you want to permanently delete this conversation? This action cannot be undone.
      </ConfirmationModal>
    </>
  );
};
