import React from 'react';
import { DivideIcon as LucideIcon } from 'lucide-react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  className?: string;
  onClick?: () => void;
  href?: string;
  type?: 'button' | 'submit' | 'reset';
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  className = '',
  onClick,
  href,
  type = 'button'
}) => {
  const baseClasses = 'font-medium inline-flex items-center justify-center rounded-md transition-all';
  
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md',
    secondary: 'bg-blue-100 hover:bg-blue-200 text-blue-900',
    outline: 'bg-transparent border border-blue-600 text-blue-600 hover:bg-blue-50',
    text: 'bg-transparent text-blue-600 hover:bg-blue-50'
  };
  
  const sizeClasses = {
    sm: 'text-sm py-1.5 px-3',
    md: 'py-2 px-4',
    lg: 'text-lg py-2.5 px-5'
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  if (href) {
    return (
      <a href={href} className={classes} onClick={onClick}>
        {Icon && <Icon className={`w-${size === 'sm' ? '4' : size === 'md' ? '5' : '6'} h-${size === 'sm' ? '4' : size === 'md' ? '5' : '6'} ${children ? 'mr-2' : ''}`} />}
        {children}
      </a>
    );
  }
  
  return (
    <button type={type} className={classes} onClick={onClick}>
      {Icon && <Icon className={`w-${size === 'sm' ? '4' : size === 'md' ? '5' : '6'} h-${size === 'sm' ? '4' : size === 'md' ? '5' : '6'} ${children ? 'mr-2' : ''}`} />}
      {children}
    </button>
  );
};

export default Button;