'use client';

import { useState, useEffect, useMemo, Fragment } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import api from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import {
  Users,
  TrendingUp,
  Target,
  BookOpen,
  Flame,
  Award,
  AlertTriangle,
  AlertCircle,
  BarChart3,
  Download,
  ChevronDown,
  ChevronUp,
  Search,
  Calendar,
  Zap,
  FileText,
  CheckCircle2,
  RefreshCw,
  ArrowRight,
  Activity,
  GraduationCap,
  Diamond,
} from 'lucide-react';

export default function TeacherDashboard() {
  const { user } = useStore();
  const [refreshKey, setRefreshKey] = useState(0);
  const [expandedStudent, setExpandedStudent] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isClient, setIsClient] = useState(false);

  // Ensure client-side rendering
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Fetch students data - always call hooks unconditionally
  const userEmail = isClient ? localStorage.getItem('user_email') : null;
  const isTeacher = userEmail === 'mathnj120@gmail.com' || user?.is_teacher;

  const { data: studentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['teacher-students', refreshKey],
    queryFn: async () => {
      try {
        const token = isClient ? localStorage.getItem('access_token') : null;
        if (!token) return { students: [], total: 0 };
        const response = await api.get('/api/v2/teacher/students', {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log('Teacher API Response:', response.data);
        return response.data;
      } catch (error: any) {
        console.error('Failed to fetch student data:', error);
        console.error('Error response:', error.response?.data);
        // Return empty data on error to prevent UI crashes
        return { students: [], total: 0 };
      }
    },
    enabled: isClient && !!user && isTeacher,
  });

  // Get real students or use empty array if none
  const realStudents = studentsData?.students || [];

  // Calculate cohort metrics from real data (client-side only to avoid hydration mismatch)
  const averageCompletion = useMemo(() =>
    realStudents.length > 0
      ? realStudents.reduce((sum: number, s: any) => sum + (s.progress?.completion_percentage || 0), 0) / realStudents.length
      : 0,
    [realStudents]
  );

  // Calculate average quiz score from real data
  const averageQuizScore = useMemo(() => {
    const allQuizScores = realStudents.flatMap((s: any) =>
      Object.values(s.quiz_scores || {}).map((q: any) => q?.score || 0)
    );
    return allQuizScores.length > 0
      ? allQuizScores.reduce((sum: number, score: number) => sum + score, 0) / allQuizScores.length
      : 0;
  }, [realStudents]);

  const activeStudentsWeekly = useMemo(() =>
    isClient ? realStudents.filter((s: any) => {
      if (!s.last_activity) return false;
      const daysSinceActivity = (Date.now() - new Date(s.last_activity).getTime()) / (1000 * 60 * 60 * 24);
      return daysSinceActivity <= 7;
    }).length : 0,
    [realStudents, isClient]
  );

  // Filter students by search
  const filteredStudents = realStudents.filter((student: any) =>
    student.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate topic difficulty from actual quiz scores
  const topicDifficultyData = useMemo(() => {
    const topicScores: Record<string, number[]> = {};
    const topicAttempts: Record<string, number> = {};

    realStudents.forEach((student: any) => {
      Object.entries(student.quiz_scores || {}).forEach(([chapterId, quizData]: [string, any]) => {
        if (!topicScores[chapterId]) {
          topicScores[chapterId] = [];
          topicAttempts[chapterId] = 0;
        }
        topicScores[chapterId].push(quizData?.score || 0);
        topicAttempts[chapterId]++;
      });
    });

    return Object.entries(topicScores)
      .map(([topic, scores]) => {
        const incorrectRate = 100 - (scores.reduce((sum, score) => sum + score, 0) / scores.length);
        return {
          topic: topic.charAt(0).toUpperCase() + topic.slice(1).replace(/chapter-\d+/i, 'Chapter'),
          incorrect_rate: Math.round(incorrectRate),
          attempts: topicAttempts[topic] || 0
        };
      })
      .filter(t => t.attempts > 0);
  }, [realStudents]);

  // Calculate drop-off analysis
  const dropOffAnalysis = useMemo(() => {
    const dropOffs: Record<string, number> = {};

    realStudents.forEach((student: any) => {
      const dropOffChapter = student.engagement?.drop_off_chapter;
      if (dropOffChapter) {
        dropOffs[dropOffChapter] = (dropOffs[dropOffChapter] || 0) + 1;
      }
    });

    return dropOffs;
  }, [realStudents]);

  // Calculate premium usage
  const totalAdaptivePaths = realStudents.reduce((sum: number, s: any) => sum + (s.premium_usage?.adaptive_paths || 0), 0);
  const totalAssessments = realStudents.reduce((sum: number, s: any) => sum + (s.premium_usage?.assessments || 0), 0);
  const totalPremiumStudents = realStudents.filter((s: any) =>
    (s.premium_usage?.adaptive_paths || 0) > 0 || (s.premium_usage?.assessments || 0) > 0
  ).length;

  // Export student data as CSV
  const handleExportCSV = () => {
    const headers = ['Student ID', 'Email', 'Completion %', 'Chapters Completed', 'Current Streak', 'Longest Streak', 'Avg Quiz Score', 'Last Activity', 'Adaptive Paths', 'Assessments'];

    const rows = realStudents.map((student: any) => {
      const quizScores = Object.values(student.quiz_scores || {});
      const avgQuiz = quizScores.length > 0 ? (quizScores.reduce((a: number, b: any) => a + (b?.score || 0), 0) / quizScores.length).toFixed(1) : 'N/A';

      return [
        student.id || 'N/A',
        student.email || 'N/A',
        student.progress?.completion_percentage || 0,
        student.progress?.chapters_completed || 0,
        student.streak?.current_streak || 0,
        student.streak?.longest_streak || 0,
        avgQuiz,
        student.last_activity ? new Date(student.last_activity).toLocaleDateString() : 'N/A',
        student.premium_usage?.adaptive_paths || 0,
        student.premium_usage?.assessments || 0,
      ].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `student-data-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Wait for client-side hydration before rendering to prevent hydration mismatch
  if (!isClient) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-4">Access Denied</h1>
            <p className="text-zinc-400">Please login to access the teacher dashboard.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isTeacher) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-4">Access Denied</h1>
            <p className="text-zinc-400 mb-4">You don&apos;t have permission to access the teacher dashboard.</p>
            <p className="text-sm text-zinc-500">Teacher access required. Contact your administrator.</p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B0C10]">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <main className="container mx-auto px-4 py-16">
          <div className="max-w-md mx-auto text-center">
            <div className="bg-zinc-900 rounded-xl p-8 border border-red-800">
              <h2 className="text-2xl font-bold text-white mb-4">Error Loading Data</h2>
              <p className="text-zinc-400 mb-4">
                Failed to load student data. Please try refreshing.
              </p>
              <p className="text-sm text-zinc-500 mb-6">
                Error: {(error as any).message || 'Unknown error'}
              </p>
              <div className="flex gap-3 justify-center">
                <Button onClick={() => refetch()}>Try Again</Button>
                <Button variant="outline" onClick={() => window.location.href('/')}>Go Home</Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }


  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Teacher Dashboard</h1>
            <p className="text-zinc-400">Monitor cohort performance, engagement, and identify students who need help</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={handleExportCSV}
              variant="secondary"
              className="hover:scale-105 active:scale-95 transition-all duration-300"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
            <Button
              onClick={() => {
                setRefreshKey(prev => prev + 1);
                refetch();
              }}
              className="bg-zinc-900 hover:bg-zinc-800 text-white hover:scale-105 active:scale-95 transition-all duration-300"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Cohort Overview */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-400" />
            Cohort Overview
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Average Completion Rate */}
            <div className="bg-teal-900/30 rounded-xl p-6 border border-cyan-500 hover-lift animate-fade-in-up">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-cyan-400" />
                <span className="text-xs text-zinc-500">Class Average</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">{averageCompletion.toFixed(1)}%</h3>
              <p className="text-sm text-zinc-400">Average completion rate</p>
            </div>

            {/* Average Quiz Score */}
            <div className="bg-teal-900/30 rounded-xl p-6 border border-cyan-500 hover-lift animate-fade-in-up delay-100">
              <div className="flex items-center justify-between mb-4">
                <Target className="w-8 h-8 text-purple-400" />
                <span className="text-xs text-zinc-500">Class Average</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">{averageQuizScore.toFixed(1)}%</h3>
              <p className="text-sm text-zinc-400">Average quiz score</p>
            </div>

            {/* Active Students */}
            <div className="bg-teal-900/30 rounded-xl p-6 border border-cyan-500 hover-lift animate-fade-in-up delay-200">
              <div className="flex items-center justify-between mb-4">
                <Flame className="w-8 h-8 text-orange-400" />
                <span className="text-xs text-zinc-500">Last 7 days</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">{activeStudentsWeekly}/{realStudents.length}</h3>
              <p className="text-sm text-zinc-400">Active students weekly</p>
            </div>

            {/* Total Students */}
            <div className="bg-teal-900/30 rounded-xl p-6 border border-cyan-500 hover-lift animate-fade-in-up delay-300">
              <div className="flex items-center justify-between mb-4">
                <GraduationCap className="w-8 h-8 text-blue-400" />
                <span className="text-xs text-zinc-500">Total</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">{realStudents.length}</h3>
              <p className="text-sm text-zinc-400">Total students</p>
            </div>
          </div>
        </div>

        {/* Student Insights */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-cyan-400" />
            Student Insights
            <span className="text-sm font-normal text-zinc-500 ml-2">
              ({filteredStudents.length} students)
            </span>
          </h2>

          {/* Search */}
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-zinc-500" />
              <input
                type="text"
                placeholder="Search by student ID or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-cyan-400 bg-zinc-900 text-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          {/* Student List */}
          <div className="bg-teal-900/30 rounded-xl border border-cyan-500 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-teal-900/50">
                  <tr className="text-left text-zinc-400">
                    <th className="px-6 py-4">Student</th>
                    <th className="px-6 py-4">Progress</th>
                    <th className="px-6 py-4">Streak</th>
                    <th className="px-6 py-4">Quiz Avg</th>
                    <th className="px-6 py-4">Last Active</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-zinc-400">
                        No students found
                      </td>
                    </tr>
                  ) : (
                    filteredStudents.map((student) => {
                      const quizScores = Object.values(student.quiz_scores || {});
                      const avgQuiz = quizScores.length > 0 ? (quizScores.reduce((a: number, b: any) => a + (b?.score || 0), 0) / quizScores.length).toFixed(1) : 'N/A';
                      const daysSinceActivity = isClient && student.last_activity ? Math.floor((Date.now() - new Date(student.last_activity).getTime()) / (1000 * 60 * 60 * 24)) : null;
                      const isExpanded = expandedStudent === student.id;

                      return (
                        <Fragment key={student.id}>
                          <tr className="border-b border-cyan-500 hover:bg-zinc-800/50 transition-colors">
                            <td className="px-6 py-4">
                              <div>
                                <p className="text-white font-medium">{student.email}</p>
                                <p className="text-xs text-zinc-500">{student.id}</p>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className="w-24 bg-zinc-800 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      (student.progress?.completion_percentage || 0) >= 80 ? 'bg-cyan-500' :
                                      (student.progress?.completion_percentage || 0) >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                    }`}
                                    style={{ width: `${student.progress?.completion_percentage || 0}%` }}
                                  />
                                </div>
                                <span className="text-sm text-zinc-400">
                                  {student.progress?.chapters_completed || 0}/{student.progress?.total_chapters || 6}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-2">
                                <Flame className={`w-4 h-4 ${(student.streak?.current_streak || 0) >= 3 ? 'text-orange-400' : 'text-zinc-400'}`} />
                                <span className="text-sm text-white">{student.streak?.current_streak || 0} day</span>
                                {(student.streak?.current_streak || 0) >= 7 && (
                                  <Award className="w-4 h-4 text-yellow-400" />
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <span className={`text-sm font-semibold ${
                                avgQuiz !== 'N/A' && parseFloat(avgQuiz) >= 80 ? 'text-cyan-400' :
                                avgQuiz !== 'N/A' && parseFloat(avgQuiz) >= 60 ? 'text-yellow-400' :
                                'text-red-400'
                              }`}>
                                {avgQuiz}%
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span className={`text-sm ${
                                daysSinceActivity === null ? 'text-zinc-500' :
                                daysSinceActivity <= 7 ? 'text-cyan-400' :
                                daysSinceActivity <= 30 ? 'text-yellow-400' : 'text-red-400'
                              }`}>
                                {daysSinceActivity === null ? 'N/A' :
                                 daysSinceActivity === 0 ? 'Today' :
                                 daysSinceActivity === 1 ? 'Yesterday' :
                                 `${daysSinceActivity} days ago`}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => setExpandedStudent(isExpanded ? null : student.id)}
                                className="hover:scale-105 active:scale-95 transition-all duration-300"
                              >
                                {isExpanded ? (
                                  <ChevronUp className="w-4 h-4" />
                                ) : (
                                  <>
                                    <ArrowRight className="w-4 h-4 mr-1" />
                                    Details
                                  </>
                                )}
                              </Button>
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr className="bg-zinc-800/50">
                              <td colSpan={6} className="px-6 py-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                  {/* Quiz Scores by Chapter */}
                                  <div>
                                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                      <Target className="w-4 h-4 text-purple-400" />
                                      Quiz Scores
                                    </h4>
                                    {quizScores.length === 0 ? (
                                      <p className="text-sm text-zinc-500">No quiz attempts yet</p>
                                    ) : (
                                      <div className="space-y-2">
                                        {Object.entries(student.quiz_scores || {}).map(([chapter, quizData]) => (
                                          <div key={chapter} className="flex items-center justify-between text-sm">
                                            <span className="text-zinc-400">{chapter}</span>
                                            <span className={`font-semibold ${
                                              (quizData?.score || 0) >= 80 ? 'text-cyan-400' : (quizData?.score || 0) >= 60 ? 'text-yellow-400' : 'text-red-400'
                                            }`}>
                                              {quizData?.score || 0}%
                                            </span>
                                          </div>
                                        ))}
                                      </div>
                                    )}
                                  </div>

                                  {/* Engagement Stats */}
                                  <div>
                                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                      <Activity className="w-4 h-4 text-blue-400" />
                                      Engagement
                                    </h4>
                                    <div className="space-y-2 text-sm">
                                      <div className="flex justify-between">
                                        <span className="text-zinc-400">Total Time</span>
                                        <span className="text-white">{student.engagement?.total_time_minutes || 0} min</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-zinc-400">Sessions</span>
                                        <span className="text-white">{student.engagement?.sessions || 0}</span>
                                      </div>
                                      {student.engagement?.drop_off_chapter && (
                                        <div className="flex justify-between">
                                          <span className="text-zinc-400">Drop-off</span>
                                          <span className="text-orange-400">{student.engagement.drop_off_chapter}</span>
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  {/* Premium Usage */}
                                  <div>
                                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                      <Zap className="w-4 h-4 text-purple-400" />
                                      Premium Features
                                    </h4>
                                    <div className="space-y-2 text-sm">
                                      <div className="flex justify-between">
                                        <span className="text-zinc-400">Adaptive Paths</span>
                                        <span className="text-white">{student.premium_usage?.adaptive_paths || 0}</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-zinc-400">Assessments</span>
                                        <span className="text-white">{student.premium_usage?.assessments || 0}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Topic Difficulty Analysis - Real Data */}
          <div className="bg-teal-900/30 rounded-xl p-8 border border-cyan-500 animate-fade-in-up">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Diamond className="w-6 h-6 text-cyan-400" />
              Topic Difficulty Analysis
            </h2>

            {topicDifficultyData.length === 0 ? (
              <p className="text-zinc-400 text-center py-8">No quiz data available yet</p>
            ) : (
              <>
                {/* Heatmap */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-white mb-4">Incorrect Rate Heatmap</h3>
                  <div className="space-y-2">
                    {topicDifficultyData
                      .sort((a, b) => b.incorrect_rate - a.incorrect_rate)
                      .slice(0, 8)
                      .map((topic) => (
                        <div key={topic.topic} className="flex items-center gap-4">
                          <div className="w-40 text-sm text-zinc-400 truncate">{topic.topic}</div>
                          <div className="flex-1 bg-zinc-800 rounded-full h-6 overflow-hidden">
                            <div
                              className={`h-6 flex items-center justify-end pr-2 transition-all ${
                                topic.incorrect_rate >= 30 ? 'bg-cyan-400' :
                                topic.incorrect_rate >= 20 ? 'bg-cyan-500' :
                                topic.incorrect_rate >= 10 ? 'bg-cyan-600' :
                                'bg-cyan-700'
                              }`}
                              style={{ width: `${Math.max(topic.incorrect_rate, 5)}%` }}
                            >
                              <span className="text-xs text-white font-semibold">{topic.incorrect_rate}%</span>
                            </div>
                          </div>
                          <div className="w-16 text-right text-sm text-zinc-500">{topic.attempts}</div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Most Difficult Concepts */}
                <div>
                  <h3 className="text-sm font-semibold text-white mb-4">Most Difficult Concepts</h3>
                  <div className="space-y-3">
                    {topicDifficultyData
                      .sort((a, b) => b.incorrect_rate - a.incorrect_rate)
                      .slice(0, 3)
                      .map((topic, index) => (
                        <div key={index} className="p-4 bg-cyan-500/10 border border-cyan-400/60 rounded-lg flex items-center justify-between">
                          <div>
                            <p className="text-white font-semibold">{topic.topic}</p>
                            <p className="text-xs text-zinc-400">{topic.attempts} attempts</p>
                          </div>
                          <div className="text-right">
                            <p className="text-cyan-400 font-bold">{topic.incorrect_rate}%</p>
                            <p className="text-xs text-zinc-500">incorrect</p>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Engagement Monitoring */}
          <div className="bg-teal-900/30 rounded-xl p-8 border border-cyan-500 animate-fade-in-up delay-100">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-400" />
              Engagement Monitoring
            </h2>

            {/* Drop-off Points */}
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-white mb-4">Drop-off Points</h3>
              <p className="text-xs text-zinc-500 mb-4">Where students stop learning</p>
              <div className="space-y-3">
                {Object.keys(dropOffAnalysis).length === 0 ? (
                  <p className="text-zinc-400 text-center py-4">No drop-offs detected!</p>
                ) : (
                  Object.entries(dropOffAnalysis)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5)
                    .map(([chapter, count]) => (
                      <div key={chapter} className="flex items-center justify-between p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                        <div className="flex items-center gap-3">
                          <AlertCircle className="w-5 h-5 text-orange-400" />
                          <span className="text-white font-semibold">{chapter}</span>
                        </div>
                        <span className="text-orange-400 font-bold">{count} students</span>
                      </div>
                    ))
                )}
              </div>
            </div>

            {/* Active vs Inactive */}
            <div>
              <h3 className="text-sm font-semibold text-white mb-4">Activity Distribution</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-cyan-500/10 border border-cyan-400/60 rounded-lg">
                  <p className="text-2xl font-bold text-cyan-400">{activeStudentsWeekly}</p>
                  <p className="text-xs text-zinc-400">Active (7d)</p>
                </div>
                <div className="text-center p-4 bg-yellow-500/10 border border-yellow-400/50 rounded-lg">
                  <p className="text-2xl font-bold text-yellow-400">
                    {isClient ? realStudents.filter((s: any) => {
                      if (!s.last_activity) return false;
                      const days = (Date.now() - new Date(s.last_activity).getTime()) / (1000 * 60 * 60 * 24);
                      return days > 7 && days <= 30;
                    }).length : 0}
                  </p>
                  <p className="text-xs text-zinc-400">At Risk (7-30d)</p>
                </div>
                <div className="text-center p-4 bg-red-500/10 border border-red-400/50 rounded-lg">
                  <p className="text-2xl font-bold text-red-400">
                    {isClient ? realStudents.filter((s: any) => {
                      if (!s.last_activity) return false;
                      const days = (Date.now() - new Date(s.last_activity).getTime()) / (1000 * 60 * 60 * 24);
                      return days > 30;
                    }).length : 0}
                  </p>
                  <p className="text-xs text-zinc-400">Inactive (&gt;30d)</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Premium Usage Analytics - Real Data */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-6 h-6 text-purple-400" />
            Premium Usage Analytics
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Adaptive Path Usage */}
            <div className="bg-teal-900/30 rounded-xl p-8 border border-cyan-500 animate-fade-in-up">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-500/20 rounded-lg">
                    <Target className="w-8 h-8 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Adaptive Paths</h3>
                    <p className="text-sm text-zinc-400">Personalized learning plans</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">{totalAdaptivePaths}</p>
                  <p className="text-sm text-zinc-500">generated</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Students using</span>
                  <span className="text-white font-semibold">
                    {realStudents.filter((s: any) => (s.premium_usage?.adaptive_paths || 0) > 0).length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Avg per student</span>
                  <span className="text-white font-semibold">
                    {realStudents.length > 0 ? (totalAdaptivePaths / realStudents.length).toFixed(1) : '0'}
                  </span>
                </div>
              </div>
            </div>

            {/* Assessment Usage */}
            <div className="bg-teal-900/30 rounded-xl p-8 border border-cyan-500 animate-fade-in-up delay-100">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-500/20 rounded-lg">
                    <FileText className="w-8 h-8 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">AI Assessments</h3>
                    <p className="text-sm text-zinc-400">Graded submissions</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">{totalAssessments}</p>
                  <p className="text-sm text-zinc-500">submitted</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Students using</span>
                  <span className="text-white font-semibold">
                    {realStudents.filter((s: any) => (s.premium_usage?.assessments || 0) > 0).length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Avg per student</span>
                  <span className="text-white font-semibold">
                    {realStudents.length > 0 ? (totalAssessments / realStudents.length).toFixed(1) : '0'}
                  </span>
                </div>
              </div>
            </div>

            {/* Total Premium Students */}
            <div className="bg-teal-900/30 rounded-xl p-8 border border-cyan-500 animate-fade-in-up delay-200">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-cyan-500/20 rounded-lg">
                    <GraduationCap className="w-8 h-8 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Premium Students</h3>
                    <p className="text-sm text-zinc-400">Using premium features</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">
                    {realStudents.filter((s: any) =>
                      (s.premium_usage?.adaptive_paths || 0) > 0 || (s.premium_usage?.assessments || 0) > 0
                    ).length}
                  </p>
                  <p className="text-sm text-zinc-500">of {realStudents.length} total</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Adaptive paths</span>
                  <span className="text-white font-semibold">
                    {realStudents.filter((s: any) => (s.premium_usage?.adaptive_paths || 0) > 0).length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Assessments</span>
                  <span className="text-white font-semibold">
                    {realStudents.filter((s: any) => (s.premium_usage?.assessments || 0) > 0).length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Both features</span>
                  <span className="text-white font-semibold">
                    {realStudents.filter((s: any) =>
                      (s.premium_usage?.adaptive_paths || 0) > 0 && (s.premium_usage?.assessments || 0) > 0
                    ).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Reports & Tools */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <Download className="w-6 h-6 text-blue-400" />
            Reports & Tools
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CSV Export */}
            <Button
              onClick={handleExportCSV}
              className="bg-teal-900/30 hover:bg-teal-900/40 border border-cyan-500 p-6 text-left hover-lift animate-fade-in-up"
            >
              <div className="flex items-center gap-4 mb-2">
                <Download className="w-8 h-8 text-blue-400" />
                <div>
                  <h3 className="text-lg font-bold text-white">Export Student Data</h3>
                  <p className="text-sm text-zinc-400">Download all student metrics as CSV</p>
                </div>
              </div>
            </Button>

            {/* Refresh Data */}
            <Button
              onClick={() => {
                setRefreshKey(prev => prev + 1);
                refetch();
              }}
              className="bg-zinc-900 hover:bg-zinc-800 border border-cyan-500 p-6 text-left hover-lift animate-fade-in-up delay-100"
            >
              <div className="flex items-center gap-4 mb-2">
                <RefreshCw className="w-8 h-8 text-cyan-400" />
                <div>
                  <h3 className="text-lg font-bold text-white">Refresh Data</h3>
                  <p className="text-sm text-zinc-400">Fetch latest student data</p>
                </div>
              </div>
            </Button>

            {/* Student Count */}
            <div className="bg-teal-900/30 border border-cyan-500 p-6 hover-lift animate-fade-in-up delay-200">
              <div className="flex items-center gap-4 mb-2">
                <Users className="w-8 h-8 text-purple-400" />
                <div>
                  <h3 className="text-lg font-bold text-white">Total Students</h3>
                  <p className="text-sm text-zinc-400">{realStudents.length} enrolled</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
