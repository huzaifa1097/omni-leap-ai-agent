'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import { onAuthStateChanged, User as FirebaseUser } from 'firebase/auth';
import { auth } from './firebase';
import { LoaderCircle } from 'lucide-react';

// Define the shape of the authentication context
interface AuthContextType {
  user: FirebaseUser | null;
  loading: boolean;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({ user: null, loading: true });

// Create a provider component that will wrap our application
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Listen for changes in the user's login state
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    // Clean up the listener when the component unmounts
    return () => unsubscribe();
  }, []);

  // Show a loading spinner while checking for a user
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <LoaderCircle className="text-white animate-spin" size={48} />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, loading: false }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a custom hook to easily access the auth context
export const useAuth = () => useContext(AuthContext);
