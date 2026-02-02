'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { getQuiz, submitQuiz } from '@/lib/api';
import { mockQuizzes } from '@/lib/mockData';
import { Quiz as QuizType, QuizAttempt } from '@/types';
import { Header } from '@/components/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export default function QuizPage() {
  const params = useParams();
  const router = useRouter();
  const chapterId = params.id as string;

  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<QuizAttempt | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);

  const { data: quiz, isLoading } = useQuery({
    queryKey: ['quiz', chapterId],
    queryFn: async () => {
      try {
        return await getQuiz(chapterId);
      } catch (err) {
        // Use mock data if API fails
        console.log('Using mock quiz data for:', chapterId);
        const mockQuiz = mockQuizzes[chapterId] || mockQuizzes['chapter-1'];
        console.log('Quiz data:', JSON.stringify(mockQuiz, null, 2));
        return mockQuiz;
      }
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    console.log('Quiz or questions not found:', { quiz, hasQuiz: !!quiz, questionsLength: quiz?.questions?.length || 0 });
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Quiz Not Found</h1>
          <p className="text-zinc-400 mb-6">The quiz for this chapter is not available yet.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={() => router.push('/')} className="btn-primary">
              Back to Home
            </button>
            <button onClick={() => router.push(`/chapters/${chapterId}`)} className="btn-secondary">
              Back to Chapter
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleAnswerChange = (questionId: string, answer: string | string[]) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    try {
      const result = await submitQuiz(quiz.id, answers);
      setResult(result);
      setSubmitted(true);
    } catch (error) {
      console.error('Failed to submit quiz, using mock result:', error);
      // Generate mock result
      const correctCount = Object.entries(answers).filter(([id, answer]) => {
        const question = quiz.questions.find(q => q.id === id);
        if (!question) return false;
        const correctAnswer = Array.isArray(question.correct_answer)
          ? answer
          : question.correct_answer;
        return answer === correctAnswer;
      }).length;

      setResult({
        id: `attempt-${Date.now()}`,
        quiz_id: quiz.id,
        user_id: 'mock-user',
        answers,
        score: Math.round((correctCount / quiz.questions.length) * 100),
        passed: (correctCount / quiz.questions.length) * 100 >= quiz.passing_score,
        submitted_at: new Date().toISOString(),
        grading_details: quiz.questions.map(q => ({
          question_id: q.id,
          correct: answers[q.id] === q.correct_answer,
          user_answer: answers[q.id] || 'Not answered',
          correct_answer: q.correct_answer,
          explanation: q.explanation,
        })),
      } as QuizAttempt);
      setSubmitted(true);
    }
  };

  if (submitted && result) {
    return <QuizResult quiz={quiz} result={result} onRetry={() => { setAnswers({}); setSubmitted(false); setResult(null); setCurrentQuestion(0); }} />;
  }

  const question = quiz.questions[currentQuestion];
  const isAnswered = answers[question.id] !== undefined;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      {/* Quiz Header */}
      <div className="border-b border-zinc-800 bg-[#0B0C10]/50 backdrop-blur">
        <div className="container px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">{quiz.title}</h1>
              <p className="text-sm text-zinc-400">Question {currentQuestion + 1} of {quiz.questions.length}</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-zinc-400">Answered</p>
                <p className="text-lg font-bold text-emerald-400">{answeredCount}/{quiz.questions.length}</p>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Quiz Content */}
      <div className="container py-8">
        <div className="max-w-3xl mx-auto">
          <Card className="glow-box">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-xl mb-2">{question.question_text}</CardTitle>
                  <CardDescription>
                    {question.question_type === 'multiple_choice' && 'Select the best answer'}
                    {question.question_type === 'true_false' && 'True or False'}
                    {question.question_type === 'short_answer' && 'Type your answer'}
                  </CardDescription>
                </div>
                <div className="ml-4 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                  <span className="text-sm font-medium text-emerald-400">{question.points} pts</span>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Debug info */}
              {process.env.NODE_ENV === 'development' && (
                <div className="text-xs text-zinc-500 mb-2">
                  Debug: question_type={question.question_type}, has_options={!!question.options}, options_count={question.options?.length || 0}
                </div>
              )}

              {question.question_type === 'multiple_choice' && question.options && question.options.length > 0 && (
                <div className="space-y-3">
                  {question.options.map((option, index) => {
                    const isSelected = answers[question.id] === option;
                    const letter = String.fromCharCode(65 + index);
                    return (
                      <button
                        key={option}
                        onClick={() => handleAnswerChange(question.id, option)}
                        className={`w-full text-left p-4 rounded-lg border transition-all ${
                          isSelected
                            ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                            : 'border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-zinc-600 hover:bg-zinc-800'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                            isSelected ? 'border-emerald-500 bg-emerald-500/20' : 'border-zinc-600'
                          }`}>
                            {isSelected && <div className="w-2 h-2 rounded-full bg-emerald-400" />}
                          </div>
                          <span className="flex-1">{option}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {question.question_type === 'true_false' && (
                <div className="grid grid-cols-2 gap-4">
                  {['True', 'False'].map((option) => {
                    const isSelected = answers[question.id] === option;
                    return (
                      <button
                        key={option}
                        onClick={() => handleAnswerChange(question.id, option)}
                        className={`p-6 rounded-lg border text-center font-medium transition-all ${
                          isSelected
                            ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                            : 'border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-zinc-600 hover:bg-zinc-800'
                        }`}
                      >
                        {option}
                      </button>
                    );
                  })}
                </div>
              )}

              {question.question_type === 'short_answer' && (
                <textarea
                  value={answers[question.id] as string || ''}
                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  placeholder="Type your answer here..."
                  className="w-full h-32 px-4 py-3 rounded-lg border border-zinc-700 bg-zinc-900 text-white placeholder:text-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              )}
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6">
            <Button
              variant="secondary"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>

            <div className="flex gap-2">
              {quiz.questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`w-10 h-10 rounded-lg border transition-all ${
                    index === currentQuestion
                      ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                      : answers[quiz.questions[index].id]
                      ? 'border-zinc-600 bg-zinc-800 text-zinc-300'
                      : 'border-zinc-800 text-zinc-600'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            {currentQuestion === quiz.questions.length - 1 ? (
              <Button
                onClick={handleSubmit}
                disabled={answeredCount === 0}
                className="gap-2"
              >
                Submit Quiz
                <CheckCircle className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={() => setCurrentQuestion(Math.min(quiz.questions.length - 1, currentQuestion + 1))}
              >
                Next
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuizResult({ quiz, result, onRetry }: { quiz: QuizType; result: QuizAttempt; onRetry: () => void }) {
  const router = useRouter();
  const score = Math.round(result.score);
  const passed = result.passed;
  const correctCount = result.grading_details.filter(d => d.correct).length;

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />

      <div className="container py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Result Header */}
          <Card className={`glow-box ${passed ? 'border-emerald-500/50' : 'border-red-500/50'}`}>
            <CardHeader className="text-center">
              <div className={`mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full ${
                passed ? 'bg-emerald-500/20' : 'bg-red-500/20'
              }`}>
                {passed ? (
                  <CheckCircle className="h-10 w-10 text-emerald-400" />
                ) : (
                  <XCircle className="h-10 w-10 text-red-400" />
                )}
              </div>
              <CardTitle className="text-2xl">
                {passed ? 'Congratulations!' : 'Keep Learning!'}
              </CardTitle>
              <CardDescription className="text-base">
                {passed
                  ? "You've mastered this chapter's content"
                  : "Review the material and try again"}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Score */}
              <div className="text-center">
                <div className={`text-5xl font-bold ${passed ? 'text-emerald-400' : 'text-red-400'}`}>
                  {score}%
                </div>
                <p className="text-zinc-400 mt-2">
                  {correctCount} of {quiz.questions.length} questions correct
                </p>
              </div>

              {/* Passing Score */}
              <div className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-400">Passing Score</span>
                  <span className="text-white font-medium">{quiz.passing_score}%</span>
                </div>
              </div>

              {/* Questions Review */}
              <div className="space-y-3">
                <h3 className="font-semibold text-white">Review Answers</h3>
                {quiz.questions.map((question, index) => {
                  const detail = result.grading_details[index];
                  return (
                    <div key={question.id} className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
                      <div className="flex items-start gap-3">
                        {detail.correct ? (
                          <CheckCircle className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 space-y-2">
                          <p className="text-sm text-white">{question.question_text}</p>
                          <div className="text-sm">
                            <p className="text-zinc-400">
                              Your answer: <span className={detail.correct ? 'text-emerald-400' : 'text-red-400'}>
                                {Array.isArray(detail.user_answer)
                                  ? detail.user_answer.join(', ')
                                  : detail.user_answer}
                              </span>
                            </p>
                            {!detail.correct && (
                              <p className="text-zinc-400">
                                Correct answer: <span className="text-emerald-400">
                                  {Array.isArray(detail.correct_answer)
                                    ? detail.correct_answer.join(', ')
                                    : detail.correct_answer}
                                </span>
                              </p>
                            )}
                          </div>
                          <p className="text-sm text-zinc-500 italic">{detail.explanation}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <Button variant="secondary" onClick={onRetry} className="flex-1">
                  Retake Quiz
                </Button>
                <Button
                  onClick={() => router.push('/')}
                  className="flex-1"
                >
                  Continue Learning
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
