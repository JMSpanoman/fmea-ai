import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-text-primary mb-1.5">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-2.5
          bg-surface-secondary border border-border rounded-lg
          text-text-primary placeholder:text-text-secondary
          focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
          transition-smooth
          ${error ? 'border-danger' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-sm text-danger">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1.5 text-sm text-text-secondary">{helperText}</p>
      )}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-text-primary mb-1.5">
          {label}
        </label>
      )}
      <textarea
        className={`
          w-full px-4 py-2.5
          bg-surface-secondary border border-border rounded-lg
          text-text-primary placeholder:text-text-secondary
          focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
          transition-smooth resize-none
          ${error ? 'border-danger' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-sm text-danger">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-1.5 text-sm text-text-secondary">{helperText}</p>
      )}
    </div>
  );
};

