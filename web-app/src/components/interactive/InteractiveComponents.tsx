'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, AlertCircle, Info, Zap, Flame } from 'lucide-react';

export function Toast() {
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>>([]);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Math.random().toString(36).substring(7);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  return (
    <>
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 100 }}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg ${
                toast.type === 'success' ? 'bg-cyan-500 text-white' :
                toast.type === 'error' ? 'bg-red-500 text-white' :
                'bg-blue-500 text-white'
              }`}
            >
              {toast.type === 'success' && <Check className="h-4 w-4" />}
              {toast.type === 'error' && <AlertCircle className="h-4 w-4" />}
              {toast.type === 'info' && <Info className="h-4 w-4" />}
              <span className="text-sm font-medium">{toast.message}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </>
  );
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 modal-backdrop"
          />
          {/* Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-zinc-900 rounded-xl border border-cyan-800 shadow-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto modal-content"
          >
            <div className="flex items-center justify-between p-6 border-b border-cyan-800">
              <h3 className="text-xl font-bold text-white">{title}</h3>
              <button
                onClick={onClose}
                className="text-zinc-400 hover:text-white hover:scale-110 transition-all duration-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-6">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface AccordionItemProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function AccordionItem({ title, children, defaultOpen = false }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-cyan-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-800/50 transition-colors duration-200"
      >
        <span className="font-medium text-white">{title}</span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <svg className="h-4 w-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 text-zinc-300">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface TabItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  children: React.ReactNode;
}

export function Tabs({ tabs, activeTab, onChange, children }: TabsProps) {
  const ActiveIcon = tabs.find(t => t.id === activeTab)?.icon;

  return (
    <div className="space-y-4">
      {/* Tab Headers */}
      <div className="flex gap-2 border-b border-cyan-800">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-2 font-medium transition-all duration-200 relative
                ${isActive ? 'text-cyan-400' : 'text-zinc-400 hover:text-white'}
              `}
            >
              {Icon && <Icon className="h-4 w-4" />}
              {tab.label}
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
                  initial={false}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div>
        {children}
      </div>
    </div>
  );
}

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  side?: 'top' | 'bottom' | 'left' | 'right';
}

export function Tooltip({ content, children, side = 'top' }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={`
              absolute z-50 px-2 py-1 text-xs text-white bg-zinc-800 rounded shadow-lg
              ${side === 'top' ? 'bottom-full mb-2 left-1/2 -translate-x-1/2' : ''}
              ${side === 'bottom' ? 'top-full mt-2 left-1/2 -translate-x-1/2' : ''}
              ${side === 'left' ? 'right-full mr-2 top-1/2 -translate-y-1/2' : ''}
              ${side === 'right' ? 'left-full ml-2 top-1/2 -translate-y-1/2' : ''}
            `}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  animated?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  label,
  showPercentage = false,
  animated = true
}: ProgressBarProps) {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex justify-between text-sm">
          <span className="text-zinc-400">{label}</span>
          {showPercentage && (
            <span className="text-zinc-300 font-medium">{percentage}%</span>
          )}
        </div>
      )}
      <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className={`h-full rounded-full ${
            animated ? 'progress-bar-animated' : 'bg-gradient-to-r from-cyan-500 to-cyan-400'
          }`}
        />
      </div>
    </div>
  );
}

interface NotificationPillProps {
  message: string;
  type?: 'info' | 'warning' | 'success';
  onClose?: () => void;
}

export function NotificationPill({ message, type = 'info', onClose }: NotificationPillProps) {
  const colors = {
    info: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    warning: 'bg-orange-500/10 border-orange-500/20 text-orange-400',
    success: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400',
  };

  const icons = {
    info: <Info className="h-4 w-4" />,
    warning: <Zap className="h-4 w-4" />,
    success: <Check className="h-4 w-4" />,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border ${colors[type]}`}
    >
      {icons[type]}
      <span className="text-sm font-medium">{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-2 hover:scale-110 transition-transform duration-200"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </motion.div>
  );
}

interface AchievementBadgeProps {
  icon: React.ReactNode;
  title: string;
  description?: string;
  unlocked?: boolean;
}

export function AchievementBadge({ icon, title, description, unlocked = true }: AchievementBadgeProps) {
  return (
    <motion.div
      whileHover={{ scale: unlocked ? 1.05 : 1 }}
      className={`
        relative p-4 rounded-xl border text-center transition-all duration-300
        ${unlocked
          ? 'bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 border-cyan-500/30 hover:border-cyan-500/50'
          : 'bg-zinc-800/50 border-cyan-700 opacity-60'
        }
      `}
    >
      <motion.div
        animate={unlocked ? { scale: [1, 1.1, 1] } : {}}
        transition={{ duration: 0.5, repeat: unlocked ? Infinity : 0 }}
        className="mb-2"
      >
        {icon}
      </motion.div>
      <h4 className={`text-sm font-bold ${unlocked ? 'text-white' : 'text-zinc-500'}`}>
        {title}
      </h4>
      {description && (
        <p className={`text-xs ${unlocked ? 'text-zinc-400' : 'text-zinc-600'}`}>
          {description}
        </p>
      )}
    </motion.div>
  );
}

interface StreakFlameProps {
  days: number;
  isOnFire?: boolean;
}

export function StreakFlame({ days, isOnFire = true }: StreakFlameProps) {
  return (
    <div className="flex items-center gap-2">
      <motion.div
        animate={isOnFire ? {
          scale: [1, 1.2, 1],
          rotate: [0, -5, 5, -5, 0],
        } : {}}
        transition={{ duration: 0.5, repeat: isOnFire ? Infinity : 0 }}
      >
        <Flame className={`h-8 w-8 ${isOnFire ? 'text-orange-400' : 'text-zinc-600'}`} />
      </motion.div>
      <div>
        <p className="text-2xl font-bold text-white">{days}</p>
        <p className="text-xs text-zinc-400">day streak</p>
      </div>
    </div>
  );
}
