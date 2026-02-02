import { ButtonHTMLAttributes, forwardRef, useState } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'default' | 'lg';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', loading = false, children, disabled, ...props }, ref) => {
    const [isClicked, setIsClicked] = useState(false);

    return (
      <button
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0B0C10] disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden',
          {
            'bg-emerald-500 hover:bg-emerald-400 text-white shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0 active:shadow-md':
              variant === 'primary',
            'bg-zinc-800 hover:bg-zinc-700 text-white hover:-translate-y-0.5 active:translate-y-0': variant === 'secondary',
            'bg-transparent text-zinc-300 hover:text-white hover:bg-zinc-800/50': variant === 'ghost',
            'border border-zinc-700 bg-transparent text-white hover:bg-zinc-800 hover:-translate-y-0.5 active:translate-y-0': variant === 'outline',
            'bg-white text-black hover:bg-zinc-200 hover:-translate-y-0.5 active:translate-y-0': variant === 'default',
          },
          {
            'h-9 px-3 text-sm': size === 'sm',
            'h-10 px-4 py-2': size === 'default',
            'h-11 px-8 text-lg': size === 'lg',
          },
          isClicked && 'scale-95',
          className
        )}
        ref={ref}
        disabled={disabled || loading}
        onClick={(e) => {
          setIsClicked(true);
          setTimeout(() => setIsClicked(false), 150);
        }}
        {...props}
      >
        {/* Ripple Effect Container */}
        <span className="absolute inset-0 ripple" />

        {/* Button Content */}
        <span className="relative flex items-center gap-2">
          {loading && (
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018 0v8H0z"></path>
            </svg>
          )}
          {children}
        </span>
      </button>
    );
  }
);

Button.displayName = 'Button';
