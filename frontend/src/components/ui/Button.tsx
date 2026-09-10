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
    primary: 'bg-brand text-white hover:bg-brand-hover focus:ring-brand',
    secondary: 'bg-white border border-gray-200 text-navy hover:bg-gray-50 focus:ring-brand',
    danger: 'bg-danger text-white hover:bg-red-600 focus:ring-danger',
    ghost: 'bg-transparent text-muted hover:bg-gray-50 hover:text-navy',
  };

  const sizes = {
    sm: 'px-3 min-h-control text-sm rounded-control',
    md: 'px-4 min-h-control text-body rounded-control',
    lg: 'px-6 min-h-control-lg text-base rounded-control',
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

