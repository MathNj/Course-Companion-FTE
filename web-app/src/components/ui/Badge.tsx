import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export const Badge = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full border border-cyan-700 px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#0B0C10]',
        className
      )}
      {...props}
    />
  )
);

Badge.displayName = 'Badge';
