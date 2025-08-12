'use client';

import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Send, Bot, User, LoaderCircle, Sparkles } from 'lucide-react';
import { useAuth } from '../../lib/auth';
import ReactMarkdown from 'react-markdown';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  imageUrl?: string;
}

interface ChatPageProps {
  sessionId: string;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

const WelcomeScreen = ({ setInput }: { setInput: (val: string) => void }) => {
    const examplePrompts = ["What's the weather in Lucknow?", "Who was Alan Turing?", "/blog The Future of AI"];
    return (
        <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="p-4 bg-gray-800 rounded-full mb-4"><Sparkles size={40} className="text-blue-400" /></div>
            <h1 className="text-2xl font-bold mb-2">OmniLeap Agent</h1>
            <p className="text-gray-400 mb-8">Your intelligent assistant is ready. Try an example:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl">
                {examplePrompts.map(prompt => (
                    <button key={prompt} onClick={() => setInput(prompt)} className="bg-gray-800 p-4 rounded-lg text-left hover:bg-gray-700 transition-colors">
                        <p className="font-semibold text-sm">{prompt}</p>
                    </button>
                ))}
            </div>
        </div>
    );
};

export const ChatPage = ({ sessionId, messages, setMessages }: ChatPageProps) => {
  const { user } = useAuth();
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // --- THIS IS THE FIX ---
  // The URL now correctly points to your local backend server
  const BACKEND_URL = 'https://omni-leap-backend-service-280476321364.asia-south1.run.app';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !user) return;

    const idToken = await user.getIdToken();
    const userMessage: Message = { id: uuidv4(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    if (currentInput.toLowerCase().startsWith('/blog ')) {
      const topic = currentInput.substring(6);
      setMessages(prev => [...prev, { id: uuidv4(), text: `Ok, dispatching my AI agent team to write a blog post about: "${topic}". This may take a few minutes...`, sender: 'agent' }]);
      
      try {
        const response = await fetch(`${BACKEND_URL}/api/v1/chat/invoke_crew`, {
          method: 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${idToken}`
          },
          body: JSON.stringify({ topic: topic }),
        });
        if (!response.ok) throw new Error('The AI crew failed to complete the task.');
        
        const data = await response.json();
        const agentMessage: Message = { id: uuidv4(), text: data.result, sender: 'agent' };
        setMessages(prev => [...prev, agentMessage]);
      
      } catch (error: any) {
        setMessages(prev => [...prev, { id: uuidv4(), text: error.message || "My agent team encountered an error.", sender: 'agent' }]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({ user_input: currentInput, session_id: sessionId }),
      });

      if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
      
      const data = await response.json();
      const agentMessage: Message = { id: uuidv4(), text: data.output, sender: 'agent' };
      if (data.output && data.output.trim().endsWith('.png')) {
          agentMessage.imageUrl = `${BACKEND_URL}/${data.output.trim()}`;
          agentMessage.text = "Here is the chart you requested:";
      }
      setMessages(prev => [...prev, agentMessage]);

    } catch (error: any) {
      console.error("API call failed:", error);
      setMessages(prev => [...prev, { id: uuidv4(), text: error.message || "Sorry, an error occurred.", sender: 'agent' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-inherit text-inherit">
      <main className="flex-1 overflow-y-auto p-4 md:p-6">
        <div className="max-w-3xl mx-auto h-full">
          {messages.length <= 1 ? (
             <WelcomeScreen setInput={setInput} />
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.sender === 'agent' && <div className="bg-blue-600 p-2 rounded-full flex-shrink-0"><Bot size={20} /></div>}
                  <div className={`prose prose-invert prose-sm px-4 py-3 rounded-2xl max-w-lg ${msg.sender === 'user' ? 'bg-gray-700 rounded-br-none' : 'bg-gray-800 rounded-bl-none'}`}>
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                    {msg.imageUrl && (
                        <div className="mt-2">
                            <img src={msg.imageUrl} alt="Generated Chart" className="rounded-lg border border-gray-700" />
                        </div>
                    )}
                  </div>
                  {msg.sender === 'user' && <div className="bg-gray-700 p-2 rounded-full flex-shrink-0"><User size={20} /></div>}
                </div>
              ))}
              {isLoading && (
                  <div className="flex items-start gap-3 justify-start">
                    <div className="bg-blue-600 p-2 rounded-full flex-shrink-0"><LoaderCircle size={20} className="animate-spin" /></div>
                    <div className="bg-gray-800 rounded-2xl rounded-bl-none px-4 py-3"><p className="text-sm">Thinking...</p></div>
                  </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>
      <footer className="bg-gray-800 border-t border-gray-700 p-4">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full bg-gray-700 text-white placeholder-gray-400 px-4 py-2 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ask a question or type /blog [topic]"
            disabled={isLoading}
          />
          <button type="submit" className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 disabled:bg-gray-600 transition-colors" disabled={isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </footer>
    </div>
  );
};
