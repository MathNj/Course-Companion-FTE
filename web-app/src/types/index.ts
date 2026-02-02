export interface User {
  id: string;
  email: string;
  subscription_type: 'free' | 'premium';
  created_at: string;
  timezone?: string;
  is_teacher?: boolean;
}

export interface Chapter {
  id: string;
  title: string;
  subtitle?: string;
  description: string;
  sections: Section[];
  learning_objectives: string[];
  estimated_time_minutes: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  access_tier: 'free' | 'premium';
  order: number;
}

export interface Section {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface Quiz {
  id: string;
  chapter_id: string;
  title: string;
  questions: Question[];
  passing_score: number;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  correct_answer: string | string[];
  explanation: string;
  points: number;
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  user_id: string;
  answers: Record<string, string | string[]>;
  score: number;
  passed: boolean;
  submitted_at: string;
  grading_details: GradingDetail[];
}

export interface GradingDetail {
  question_id: string;
  correct: boolean;
  user_answer: string | string[];
  correct_answer: string | string[];
  explanation: string;
}

export interface Progress {
  user_id: string;
  chapters_completed: number;
  total_chapters: number;
  completion_percentage: number;
  quiz_scores: Record<string, number>;
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  last_activity_date: string;
  chapter_progress: ChapterProgress[];
}

export interface ChapterProgress {
  chapter_id: string;
  completion_status: 'not_started' | 'in_progress' | 'completed';
  completion_percent?: number;
  quiz_score?: number;
  time_spent_minutes: number;
  last_accessed: string;
}

export interface Streak {
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string;
  timezone: string;
}

export interface AdaptivePath {
  learning_path: {
    current_status: string;
    recommended_next: RecommendedChapter[];
    knowledge_gaps: KnowledgeGap[];
    study_plan: StudyPlan;
    motivation: string;
  };
  tokens_used: number;
  cost_usd: number;
  generated_at: string;
}

export interface RecommendedChapter {
  chapter: number;
  title: string;
  reason: string;
  priority: 'high' | 'medium' | 'low';
  estimated_difficulty: string;
}

export interface KnowledgeGap {
  topic: string;
  gap_severity: 'minor' | 'moderate' | 'significant';
  recommended_resources: string[];
}

export interface StudyPlan {
  this_week: string[];
  next_week: string[];
}

export interface AssessmentFeedback {
  score: number;
  feedback: {
    strengths: string[];
    areas_for_improvement: string[];
    specific_suggestions: string[];
  };
  rubric_scores: Record<string, number>;
  tokens_used: number;
  cost_usd: number;
  graded_at: string;
}
