import React, { useEffect } from 'react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  position?: 'left' | 'right';
  width?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  position = 'right',
  width = '400px',
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      
      {/* Drawer */}
      <div
        className={`
          relative z-10 h-full
          bg-surface-primary border-${position === 'right' ? 'l' : 'r'} border-border
          shadow-elevated
          flex flex-col
          transition-smooth-slow
          ${position === 'right' ? 'ml-auto' : 'mr-auto'}
        `}
        style={{ width }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        {title && (
          <div className="px-6 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-h2 text-text-primary font-semibold">{title}</h2>
            <button
              onClick={onClose}
              className="text-text-secondary hover:text-text-primary transition-smooth"
            >
              ✕
            </button>
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
      </div>
    </div>
  );
};

