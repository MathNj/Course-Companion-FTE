import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export const Progress = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement> & { value?: number }>(
  ({ className, value = 0, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('relative h-4 w-full overflow-hidden rounded-full bg-zinc-800', className)}
      {...props}
    >
      <div
        className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-500"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
);

Progress.displayName = 'Progress';
