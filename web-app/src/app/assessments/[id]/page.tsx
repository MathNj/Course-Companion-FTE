'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store/useStore';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Header } from '@/components/Header';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import {
  FileText,
  Send,
  AlertCircle,
  CheckCircle2,
  Clock,
  Target
} from 'lucide-react';

export default function AssessmentSubmitPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useStore();
  const chapterId = params.id as string;

  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [rubric, setRubric] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Mock assessment data (in production, fetch from API)
  const assessmentData = {
    chapterId,
    questionType: 'short_answer',
    questionText: 'Explain the key differences between supervised and unsupervised learning in machine learning.',
    rubric: 'Answer should clearly define both types, provide examples of each, and explain the key difference in terms of labeled vs unlabeled data.',
    wordLimit: 500,
  };

  const wordCount = answer.trim().split(/\s+/).filter(word => word.length > 0).length;
  const isValid = question.length > 0 && answer.length > 0 && rubric.length > 0 && wordCount <= assessmentData.wordLimit;

  const handleSubmit = async () => {
    if (!isValid) {
      setError('Please fill in all fields and stay within the word limit.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await api.post('/api/v2/premium/assessments/grade', {
        question: question || assessmentData.questionText,
        student_answer: answer,
        rubric: rubric || assessmentData.rubric,
        question_type: assessmentData.questionType,
      });

      // Show success and redirect to dashboard
      alert('Assessment submitted successfully! Check your dashboard for feedback.');
      router.push('/dashboard');
    } catch (err: any) {
      // Show fallback UI for demo
      console.log('Backend not available, showing demo mode');
      alert('Assessment submitted! (Demo mode - backend API unavailable)');
      router.push('/dashboard');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Header />
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-4">Assessment Not Available</h1>
            <p className="text-zinc-400">Please login to access assessments.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold text-white mb-2">AI Assessment</h1>
          <p className="text-zinc-400">Submit your work for personalized AI feedback and grading</p>
        </div>

        {/* Premium Notice */}
        <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl p-6 border border-purple-500/30 mb-8 animate-fade-in-up">
          <div className="flex items-start gap-4">
            <Target className="w-8 h-8 text-purple-400 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Premium Feature</h3>
              <p className="text-zinc-300 mb-3">
                Get instant, detailed feedback on your work using advanced AI. Our AI analyzes your answers,
                provides specific improvements, and helps you learn more effectively.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="flex items-center gap-2 text-sm text-zinc-400">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  <span>Detailed grading</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-zinc-400">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  <span>Personalized feedback</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-zinc-400">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  <span>Actionable insights</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Assessment Form */}
        <div className="bg-zinc-900 rounded-xl p-8 border border-cyan-800 animate-fade-in-up">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Assessment Submission</h2>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <p className="text-red-400">{error}</p>
              </div>
            </div>
          )}

          <div className="space-y-6">
            {/* Question */}
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Question
              </label>
              <textarea
                value={question || assessmentData.questionText}
                onChange={(e) => setQuestion(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-cyan-700 bg-zinc-800 text-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                placeholder="Enter your question here..."
              />
              <p className="text-xs text-zinc-500 mt-1">The question you want to answer</p>
            </div>

            {/* Your Answer */}
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Your Answer <span className="text-zinc-500">(required)</span>
              </label>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                rows={10}
                className="w-full px-4 py-3 rounded-lg border border-cyan-700 bg-zinc-800 text-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                placeholder="Write your answer here..."
              />
              <div className="flex items-center justify-between mt-2">
                <p className="text-sm text-zinc-400">Word count: {wordCount} / {assessmentData.wordLimit}</p>
                {wordCount > assessmentData.wordLimit && (
                  <p className="text-sm text-red-400">Over limit by {wordCount - assessmentData.wordLimit} words</p>
                )}
              </div>
            </div>

            {/* Grading Rubric */}
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Grading Rubric <span className="text-zinc-500">(required)</span>
              </label>
              <textarea
                value={rubric || assessmentData.rubric}
                onChange={(e) => setRubric(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-cyan-700 bg-zinc-800 text-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                placeholder="Describe how this should be graded..."
              />
              <p className="text-xs text-zinc-500 mt-1">
                What criteria should be used to evaluate your answer?
              </p>
            </div>

            {/* Info Box */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-white mb-1">How AI Grading Works</h4>
                  <p className="text-xs text-zinc-400">
                    Our AI analyzes your answer against the rubric, provides detailed feedback on strengths
                    and areas for improvement, and assigns a score. This typically takes 5-10 seconds.
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-between pt-4 border-t border-cyan-800">
              <div className="text-sm text-zinc-500">
                <Clock className="w-4 h-4 inline mr-1" />
                Estimated time: 5-10 seconds
              </div>
              <Button
                onClick={handleSubmit}
                disabled={!isValid || isSubmitting}
                className="min-w-[150px] hover:scale-105 active:scale-95 transition-all duration-300"
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 w-4 h-4" />
                    Submit for Grading
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Example Assessment */}
        <div className="mt-8 bg-zinc-900 rounded-xl p-8 border border-cyan-800 animate-fade-in-up delay-100">
          <h3 className="text-xl font-bold text-white mb-4">Example Assessment</h3>
          <div className="space-y-4 text-zinc-300">
            <div>
              <p className="text-sm font-semibold text-white mb-2">Question:</p>
              <p className="text-sm">{assessmentData.questionText}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-white mb-2">Sample Rubric:</p>
              <p className="text-sm">{assessmentData.rubric}</p>
            </div>
            <div className="bg-zinc-800 rounded-lg p-4">
              <p className="text-sm font-semibold text-white mb-2">Sample Good Answer:</p>
              <p className="text-sm">
                &quot;Supervised learning uses labeled data to train models, meaning the input data comes
                with the correct output. Examples include classification (spam detection) and regression
                (price prediction). Unsupervised learning finds patterns in unlabeled data without
                predefined outputs, such as clustering (customer segmentation) and dimensionality
                reduction (PCA). The key difference is that supervised learning learns from labeled
                examples while unsupervised learning discovers hidden structures in unlabeled data.&quot;
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
