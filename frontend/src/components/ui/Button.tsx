import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  className = '',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-smooth focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface-primary';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-hover focus:ring-primary shadow-elevated hover:shadow-glow',
    secondary: 'bg-transparent border-2 border-primary text-primary hover:bg-primary/10 focus:ring-primary',
    danger: 'bg-danger text-white hover:bg-red-600 focus:ring-danger',
    ghost: 'bg-transparent text-text-secondary hover:bg-surface-secondary hover:text-text-primary',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 text-body rounded-button',
    lg: 'px-6 py-3 text-base rounded-button',
  };

  return (
    <button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {icon && <span className={children ? 'mr-2' : ''}>{icon}</span>}
      {children}
    </button>
  );
};

