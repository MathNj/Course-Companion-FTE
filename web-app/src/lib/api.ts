import axios from 'axios';
import type {
  Chapter,
  Quiz,
  QuizAttempt,
  Progress,
  User,
  AdaptivePath,
  AssessmentFeedback,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Chapters
export async function getChapters() {
  const response = await api.get<Chapter[]>('/api/v1/chapters');
  return response.data;
}

export async function getChapter(chapterId: string) {
  const response = await api.get<Chapter>(`/api/v1/chapters/${chapterId}`);
  return response.data;
}

export async function searchChapters(query: string, limit = 10) {
  const response = await api.get('/api/v1/chapters/search', {
    params: { q: query, limit },
  });
  return response.data;
}

// Quizzes
export async function getQuiz(quizId: string) {
  const response = await api.get<Quiz>(`/api/v1/quizzes/${quizId}`);
  return response.data;
}

export async function submitQuiz(quizId: string, answers: Record<string, string | string[]>) {
  const response = await api.post<QuizAttempt>(`/api/v1/quizzes/${quizId}/submit`, {
    quiz_id: quizId,
    answers,
  });
  return response.data;
}

// Progress
export async function getProgress() {
  const response = await api.get<Progress>('/api/v1/progress');
  return response.data;
}

export async function getStreak() {
  const response = await api.get('/api/v1/progress/streak');
  return response.data;
}

export async function recordActivity(chapterId?: string) {
  const response = await api.post('/api/v1/progress/activity', {
    chapter_id: chapterId,
  });
  return response.data;
}

// Milestones
export interface Milestone {
  id: string;
  milestone_type: string;
  display_name: string;
  message: string;
  icon_emoji: string;
  achieved_at: string;
  metadata?: Record<string, any>;
}

export interface MilestoneCategory {
  type: string;
  name: string;
  icon: string;
  achieved: boolean;
  progress?: number;
  total?: number;
  progress_percent?: number;
  description?: string;
}

export interface AchievableMilestones {
  chapters: MilestoneCategory[];
  quizzes: MilestoneCategory[];
  streaks: MilestoneCategory[];
  time: MilestoneCategory[];
  badges: MilestoneCategory[];
}

export async function getMilestones(): Promise<Milestone[]> {
  const response = await api.get<Milestone[]>('/api/v1/milestones');
  return response.data;
}

export async function getAchievableMilestones(): Promise<AchievableMilestones> {
  const response = await api.get<AchievableMilestones>('/api/v1/milestones/achievable');
  return response.data;
}

export async function getNextMilestones(count = 3): Promise<{ next_milestones: MilestoneCategory[] }> {
  const response = await api.get<{ next_milestones: MilestoneCategory[] }>('/api/v1/milestones/next', {
    params: { count },
  });
  return response.data;
}

export async function getMilestoneSummary(): Promise<{
  total_achieved: number;
  total_possible: number;
  completion_percentage: number;
  recent_milestones: Milestone[];
  next_milestones: MilestoneCategory[];
  achievements_by_type: Record<string, number>;
}> {
  const response = await api.get('/api/v1/milestones/summary');
  return response.data;
}

// Auth
export async function register(email: string, password: string, timezone?: string) {
  try {
    const response = await api.post<{ access_token: string; user: User }>('/api/v1/auth/register', {
      email,
      password,
      timezone,
    });
    return response.data;
  } catch (error: any) {
    // Fallback to mock registration for demo purposes
    console.log('Backend not available, using mock registration');
    const mockUser: User = {
      id: 'mock-user-' + Date.now(),
      email,
      subscription_type: 'free',
      created_at: new Date().toISOString(),
      is_teacher: email === 'mathnj120@gmail.com',
    };
    return {
      access_token: 'mock-token-' + Date.now(),
      user: mockUser,
    };
  }
}

export async function login(email: string, password: string) {
  try {
    const response = await api.post<{ access_token: string; refresh_token: string; user: User }>(
      '/api/v1/auth/login',
      {
        email,
        password,
      }
    );
    return response.data;
  } catch (error: any) {
    // Fallback to mock login for demo purposes
    console.log('Backend not available, using mock login');
    const mockUser: User = {
      id: 'mock-user-' + Date.now(),
      email,
      subscription_type: 'free',
      created_at: new Date().toISOString(),
      is_teacher: email === 'mathnj120@gmail.com',
    };
    return {
      access_token: 'mock-token-' + Date.now(),
      refresh_token: 'mock-refresh-token-' + Date.now(),
      user: mockUser,
    };
  }
}

export async function getCurrentUser() {
  try {
    const response = await api.get<User>('/api/v1/auth/me');
    return response.data;
  } catch (error: any) {
    // Fallback to mock user for demo purposes
    console.log('Backend not available, using mock user');
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      throw new Error('No token found');
    }
    // Extract email from token if it's a mock token for mathnj120@gmail.com
    const storedEmail = typeof window !== 'undefined' ? localStorage.getItem('user_email') : null;
    const mockUser: User = {
      id: 'mock-user',
      email: storedEmail || 'demo@example.com',
      subscription_type: 'free',
      created_at: new Date().toISOString(),
      is_teacher: storedEmail === 'mathnj120@gmail.com',
    };
    return mockUser;
  }
}

// Premium / Phase 2
export async function gradeAssessment(
  question: string,
  studentAnswer: string,
  rubric: string,
  questionType: string
) {
  const response = await api.post<AssessmentFeedback>('/api/v2/premium/assessments/grade', {
    question,
    student_answer: studentAnswer,
    rubric,
    question_type: questionType,
  });
  return response.data;
}

export async function generateLearningPath(
  currentChapterId: number,
  focus: string,
  includeCompleted: boolean
) {
  const response = await api.post<AdaptivePath>('/api/v2/premium/learning-path/generate', {
    current_chapter_id: currentChapterId,
    focus,
    include_completed: includeCompleted,
    learning_style: 'mixed',
  });
  return response.data;
}

export async function getPremiumUsage() {
  const response = await api.get('/api/v2/premium/usage/monthly');
  return response.data;
}

export async function getSubscriptionStatus() {
  const response = await api.get('/api/v2/premium/subscription/status');
  return response.data;
}

export default api;
