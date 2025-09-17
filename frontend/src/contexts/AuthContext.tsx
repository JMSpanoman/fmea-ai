import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import emailRepository from '../services/emailRepository';
import emailNotificationService from '../services/emailNotificationService';

interface User {
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
    const savedEmail = localStorage.getItem('userEmail');
    if (savedEmail) {
      setUser({ email: savedEmail });
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string): Promise<void> => {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new Error('Please enter a valid email address');
    }

    // Check if email is authorized
    const authorizedUser = emailRepository.getEmailByAddress(email);
    if (!authorizedUser || !authorizedUser.isActive) {
      throw new Error('This email address is not authorized to access the system or is inactive. Please contact your administrator.');
    }

    // Store user email in localStorage
    localStorage.setItem('userEmail', email);
    setUser({ email: authorizedUser.email, name: authorizedUser.name });

    // Send login notification to admin
    try {
      await emailNotificationService.sendLoginNotification({
        userEmail: authorizedUser.email,
        userName: authorizedUser.name || 'Unknown',
        userRole: authorizedUser.role || 'User',
        loginTime: new Date().toLocaleString(),
        ipAddress: 'Unknown', // In a real app, you'd get this from the request
        userAgent: navigator.userAgent
      });
    } catch (error) {
      console.error('Failed to send login notification:', error);
      // Don't fail login if notification fails
    }
  };

  const logout = () => {
    localStorage.removeItem('userEmail');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
