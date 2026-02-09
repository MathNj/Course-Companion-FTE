'use client';

import { useState } from 'react';
import { Chapter, Quiz } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Sparkles, Brain, TrendingUp, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { AIChat } from './AIChat';

interface AIAssistantProps {
  chapter: Chapter;
  quiz?: Quiz;
}

export function AIAssistant({ chapter, quiz }: AIAssistantProps) {
  const { user, setShowUpgradeModal } = useStore();
  const isPremium = user?.subscription_tier === 'premium';
  const [showChat, setShowChat] = useState(false);

  return (
    <div className="space-y-4">
      {/* AI Assistant Card */}
      {!showChat ? (
        <Card className="glow-box">
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                <Sparkles className="h-4 w-4 text-cyan-400" />
              </div>
              <CardTitle className="text-lg">AI Assistant</CardTitle>
            </div>
            <CardDescription>
              Get personalized help with this chapter
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Ask Question - Opens Chat */}
            <Button
              variant="secondary"
              className="w-full gap-2"
              onClick={() => setShowChat(true)}
            >
              <MessageSquare className="h-4 w-4" />
              Ask a Question
            </Button>

            {/* Premium Features */}
            {isPremium ? (
              <div className="space-y-2 pt-2">
                <Link href={`/chapters/${chapter.id}/adaptive-path`}>
                  <Button variant="outline" className="w-full gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Get Adaptive Path
                  </Button>
                </Link>
                <Link href={`/chapters/${chapter.id}/assessments`}>
                  <Button variant="outline" className="w-full gap-2">
                    <Brain className="h-4 w-4" />
                    AI Assessment
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-gradient-to-br from-cyan-500/5 to-cyan-500/10 border border-cyan-500/10">
                <p className="text-xs text-zinc-400 mb-2">Unlock premium AI features:</p>
                <ul className="space-y-1 text-xs text-zinc-300">
                  <li>• Personalized learning paths</li>
                  <li>• AI-graded assessments</li>
                  <li>• Detailed feedback</li>
                </ul>
                <Button size="sm" className="w-full mt-3" onClick={() => setShowUpgradeModal(true)}>
                  View Plans
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        /* Chat Interface */
        <div className="space-y-2">
          <AIChat chapter={chapter} isOpen={showChat} onClose={() => setShowChat(false)} />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowChat(false)}
            className="w-full text-zinc-400 hover:text-white"
          >
            <ChevronUp className="h-4 w-4 mr-2" />
            Collapse Chat
          </Button>
        </div>
      )}

      {/* Chapter Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Chapter Info</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-zinc-400">Difficulty</span>
            <span className="text-white capitalize">{chapter.difficulty}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-400">Duration</span>
            <span className="text-white">{chapter.estimated_time}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-400">Content</span>
            <span className="text-white">
              {chapter.sections && Array.isArray(chapter.sections) && chapter.sections.length > 0
                ? `${chapter.sections.length} sections`
                : chapter.content
                ? 'Full chapter'
                : 'No content'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-400">Access</span>
            <span className={`capitalize ${chapter.access_tier === 'premium' ? 'text-cyan-400' : 'text-zinc-300'}`}>
              {chapter.access_tier}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {quiz && (
            <Link href={`/chapters/${chapter.id}/quiz`}>
              <Button variant="outline" size="sm" className="w-full justify-start">
                Take Chapter Quiz
              </Button>
            </Link>
          )}
          <Button variant="outline" size="sm" className="w-full justify-start" disabled>
            Download Notes (Coming Soon)
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start" disabled>
            Bookmark Section (Coming Soon)
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
