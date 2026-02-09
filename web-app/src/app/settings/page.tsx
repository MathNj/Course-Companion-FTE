'use client';

import { useState } from 'react';
import { useStore } from '@/store/useStore';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import {
  User,
  Mail,
  Lock,
  Bell,
  Palette,
  Save,
  Shield,
  Trash2,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Crown,
  Zap,
} from 'lucide-react';
import Link from 'next/link';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

type SettingsSection = 'profile' | 'security' | 'notifications' | 'preferences' | 'danger';

interface UpdateProfileData {
  email?: string;
  timezone?: string;
}

interface ChangePasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export default function SettingsPage() {
  const { user, logout } = useStore();
  const router = useRouter();
  const [expandedSection, setExpandedSection] = useState<SettingsSection>('profile');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('');

  // Profile form state
  const [email, setEmail] = useState(user?.email || '');
  const [timezone, setTimezone] = useState(user?.timezone || 'UTC');

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Notification preferences
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [streakReminders, setStreakReminders] = useState(true);
  const [weeklyReport, setWeeklyReport] = useState(true);

  // Learning preferences
  const [dailyGoalMinutes, setDailyGoalMinutes] = useState(30);
  const [reminderTime, setReminderTime] = useState('09:00');

  useEffect(() => {
    setEmail(user?.email || '');
    setTimezone(user?.timezone || 'UTC');
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Sign In Required</h1>
          <p className="text-zinc-400 mb-8">Please sign in to access your settings</p>
          <Link href="/login">
            <Button>Sign In</Button>
          </Link>
        </div>
      </div>
    );
  }

  const handleUpdateProfile = async () => {
    setSaveStatus('saving');
    try {
      // Call the API to update profile
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ email, timezone }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update profile');
      }

      // Update user in store
      const updatedUser = await response.json();
      // Update store with new user data if needed
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('user_email', email);
      }

      setSaveStatus('success');
      setSaveMessage('Profile updated successfully');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error: any) {
      setSaveStatus('error');
      setSaveMessage(error.message || 'Failed to update profile');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setSaveStatus('error');
      setSaveMessage('New passwords do not match');
      setTimeout(() => setSaveStatus('idle'), 3000);
      return;
    }

    if (newPassword.length < 8) {
      setSaveStatus('error');
      setSaveMessage('Password must be at least 8 characters');
      setTimeout(() => setSaveStatus('idle'), 3000);
      return;
    }

    setSaveStatus('saving');
    try {
      // Call the API to change password
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }

      setSaveStatus('success');
      setSaveMessage('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error: any) {
      setSaveStatus('error');
      setSaveMessage(error.message || 'Failed to change password');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone and all your progress will be lost.'
    );

    if (!confirmed) return;

    const doubleConfirmed = window.confirm(
      'This is your last chance! Deleting your account will permanently remove:\n\n' +
      '• All progress data\n' +
      '• Quiz scores and certificates\n' +
      '• Streaks and milestones\n' +
      '• Notes and bookmarks\n\n' +
      'Click OK to confirm account deletion.'
    );

    if (!doubleConfirmed) return;

    try {
      // Call the API to delete account
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/me`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete account');
      }

      // Logout and redirect to home
      logout();
      router.push('/');
    } catch (error: any) {
      alert(error.message || 'Failed to delete account. Please contact support.');
    }
  };

  const toggleSection = (section: SettingsSection) => {
    setExpandedSection(expandedSection === section ? 'profile' : section);
  };

  const SectionCard = ({
    id,
    title,
    icon: Icon,
    children,
  }: {
    id: SettingsSection;
    title: string;
    icon: any;
    children: React.ReactNode;
  }) => {
    const isExpanded = expandedSection === id;

    return (
      <div className="card-dark">
        <button
          onClick={() => toggleSection(id)}
          className="w-full flex items-center justify-between p-6 text-left"
        >
          <div className="flex items-center gap-3">
            <Icon className="h-5 w-5 text-cyan-400" />
            <h3 className="text-lg font-semibold text-white">{title}</h3>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-zinc-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-zinc-400" />
          )}
        </button>

        {isExpanded && <div className="px-6 pb-6 border-t border-cyan-800 pt-6">{children}</div>}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
            <p className="text-zinc-400">Manage your account and preferences</p>
          </div>
        </div>

        {/* Settings Sections */}
        <div className="space-y-4 max-w-3xl">
          {/* Profile Section */}
          <SectionCard id="profile" title="Profile" icon={User}>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Subscription Plan
                </label>
                <div className="flex items-center justify-between p-4 bg-zinc-900 rounded-lg border border-cyan-800">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      user.subscription_tier === 'free'
                        ? 'bg-zinc-700'
                        : user.subscription_tier === 'premium' || user.subscription_tier === 'pro'
                        ? 'bg-purple-500/20'
                        : 'bg-yellow-500/20'
                    }`}>
                      <Crown className={`h-5 w-5 ${
                        user.subscription_tier === 'free'
                          ? 'text-zinc-400'
                          : user.subscription_tier === 'premium' || user.subscription_tier === 'pro'
                          ? 'text-purple-400'
                          : 'text-yellow-400'
                      }`} />
                    </div>
                    <div>
                      <p className="text-white font-medium capitalize">
                        {user.subscription_tier === 'pro' ? 'Pro' : user.subscription_tier === 'premium' ? 'Premium' : 'Free'}
                      </p>
                      <p className="text-sm text-zinc-500">
                        {user.subscription_tier === 'free' && 'Basic access'}
                        {user.subscription_tier === 'premium' && 'Full course access'}
                        {user.subscription_tier === 'pro' && 'All features + priority'}
                      </p>
                    </div>
                  </div>
                  {user.subscription_tier === 'free' && (
                    <Link href="/pricing">
                      <Button size="sm" variant="outline" className="border-purple-500 text-purple-400 hover:bg-purple-500/10">
                        Upgrade Plan
                      </Button>
                    </Link>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Email Address
                </label>
                <div className="flex gap-3">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="flex-1 px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
                    placeholder="your@email.com"
                  />
                  <Button
                    onClick={handleUpdateProfile}
                    disabled={saveStatus === 'saving'}
                    className="min-w-fit"
                  >
                    {saveStatus === 'saving' ? (
                      <LoadingSpinner size="small" />
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Timezone
                </label>
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                >
                  <option value="UTC">UTC (Coordinated Universal Time)</option>
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  <option value="Europe/London">London (GMT)</option>
                  <option value="Europe/Paris">Central European (CET)</option>
                  <option value="Asia/Kolkata">India (IST)</option>
                  <option value="Asia/Tokyo">Japan (JST)</option>
                  <option value="Australia/Sydney">Sydney (AEDT)</option>
                </select>
              </div>
            </div>
          </SectionCard>

          {/* Security Section */}
          <SectionCard id="security" title="Security" icon={Lock}>
            <div className="space-y-6">
              <div className="flex items-center gap-3 p-4 bg-zinc-900 rounded-lg border border-cyan-800">
                <Shield className="h-5 w-5 text-zinc-400" />
                <div>
                  <p className="text-sm text-zinc-400">Password last changed</p>
                  <p className="text-white font-medium">Recently</p>
                </div>
              </div>

              <div>
                <h4 className="text-white font-medium mb-4">Change Password</h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
                      placeholder="Enter current password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
                      placeholder="Enter new password (min 8 characters)"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white placeholder:text-zinc-500 focus:border-cyan-500 focus:outline-none"
                      placeholder="Confirm new password"
                    />
                  </div>
                  <Button
                    onClick={handleChangePassword}
                    disabled={saveStatus === 'saving' || !currentPassword || !newPassword}
                    className="w-full"
                  >
                    {saveStatus === 'saving' ? (
                      <LoadingSpinner size="small" />
                    ) : (
                      'Change Password'
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </SectionCard>

          {/* Notifications Section */}
          <SectionCard id="notifications" title="Notifications" icon={Bell}>
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-zinc-900 rounded-lg border border-cyan-800">
                <div>
                  <p className="text-white font-medium">Email Notifications</p>
                  <p className="text-sm text-zinc-500">Receive updates about your progress</p>
                </div>
                <button
                  onClick={() => setEmailNotifications(!emailNotifications)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    emailNotifications ? 'bg-cyan-600' : 'bg-zinc-700'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                      emailNotifications ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-zinc-900 rounded-lg border border-cyan-800">
                <div>
                  <p className="text-white font-medium">Streak Reminders</p>
                  <p className="text-sm text-zinc-500">Get reminded to maintain your streak</p>
                </div>
                <button
                  onClick={() => setStreakReminders(!streakReminders)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    streakReminders ? 'bg-cyan-600' : 'bg-zinc-700'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                      streakReminders ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-zinc-900 rounded-lg border border-cyan-800">
                <div>
                  <p className="text-white font-medium">Weekly Progress Report</p>
                  <p className="text-sm text-zinc-500">Summary of your weekly learning activity</p>
                </div>
                <button
                  onClick={() => setWeeklyReport(!weeklyReport)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    weeklyReport ? 'bg-cyan-600' : 'bg-zinc-700'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                      weeklyReport ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
              </div>
            </div>
          </SectionCard>

          {/* Learning Preferences */}
          <SectionCard id="preferences" title="Learning Preferences" icon={Zap}>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Daily Learning Goal
                </label>
                <select
                  value={dailyGoalMinutes}
                  onChange={(e) => setDailyGoalMinutes(parseInt(e.target.value))}
                  className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={45}>45 minutes</option>
                  <option value={60}>60 minutes</option>
                  <option value={90}>90 minutes</option>
                </select>
                <p className="text-sm text-zinc-500 mt-1">Recommended daily learning time</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Preferred Reminder Time
                </label>
                <input
                  type="time"
                  value={reminderTime}
                  onChange={(e) => setReminderTime(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-900 border border-cyan-700 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                />
                <p className="text-sm text-zinc-500 mt-1">When to send daily learning reminders</p>
              </div>
            </div>
          </SectionCard>

          {/* Danger Zone */}
          <SectionCard id="danger" title="Danger Zone" icon={AlertCircle}>
            <div className="space-y-4">
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-white font-medium mb-2">Delete Account</p>
                <p className="text-sm text-zinc-400 mb-4">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
                <Button
                  onClick={handleDeleteAccount}
                  variant="outline"
                  className="border-red-500 text-red-400 hover:bg-red-500 hover:text-white"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Save Status Banner */}
        {saveStatus !== 'idle' && (
          <div className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg flex items-center gap-3 ${
            saveStatus === 'success' ? 'bg-cyan-600 text-white' : 'bg-red-600 text-white'
          }`}>
            {saveStatus === 'success' ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{saveMessage}</span>
          </div>
        )}
      </main>
    </div>
  );
}
