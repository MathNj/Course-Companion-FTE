"""
LLM Service for Phase 2 Hybrid Intelligence Features

This service provides LLM capabilities for premium features:
- LLM-Graded Assessments
- Adaptive Learning Paths
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from openai import AsyncOpenAI


class LLMService:
    """Service for LLM API calls (Phase 2 hybrid features)"""

    def __init__(self, db: Session = None):
        self.db = db

        # LLM Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        # Determine if using real API or mock mode
        self.mock_mode = not bool(self.openai_api_key)

        # Initialize OpenAI client if API key is available
        if not self.mock_mode:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None

        # Cost tracking for GPT-4o (per 1M tokens)
        self.cost_per_million_input = 2.50  # GPT-4o input
        self.cost_per_million_output = 10.00  # GPT-4o output

    async def grade_assessment(
        self,
        question: str,
        student_answer: str,
        rubric: str,
        question_type: str = "short_answer",
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Grade free-form assessment using LLM (or mock response)

        Args:
            question: The question being asked
            student_answer: The student's free-form answer
            rubric: Grading rubric/scheme
            question_type: Type of question (short_answer, essay, code_explanation)
            user_id: User ID for cost tracking

        Returns:
            Dict with score, feedback, and cost tracking
        """

        if self.mock_mode:
            return await self._mock_grade_assessment(
                question=question,
                student_answer=student_answer,
                rubric=rubric,
                question_type=question_type,
                user_id=user_id
            )
        else:
            return await self._real_grade_assessment(
                question=question,
                student_answer=student_answer,
                rubric=rubric,
                question_type=question_type,
                user_id=user_id
            )

    async def _mock_grade_assessment(
        self,
        question: str,
        student_answer: str,
        rubric: str,
        question_type: str,
        user_id: int
    ) -> Dict[str, Any]:
        """Mock assessment grading (Phase 2A)"""

        # Simulate realistic scoring
        base_score = random.randint(70, 95)

        # Generate detailed feedback
        feedback = {
            "strengths": self._generate_strengths(question, student_answer),
            "areas_for_improvement": self._generate_improvements(question, student_answer),
            "specific_suggestions": self._generate_suggestions(question, student_answer)
        }

        # Parse rubric and generate category scores
        rubric_scores = self._parse_rubric_scores(rubric, base_score)

        # Calculate token usage (simulated)
        input_tokens = len(question.split()) + len(student_answer.split()) + len(rubric.split())
        output_tokens = 500  # Estimated for feedback
        total_tokens = input_tokens + output_tokens

        # Calculate cost
        cost_usd = self._calculate_cost(input_tokens, output_tokens)

        result = {
            "score": base_score,
            "feedback": feedback,
            "rubric_scores": rubric_scores,
            "tokens_used": total_tokens,
            "cost_usd": round(cost_usd, 4),
            "model_name": self.default_model,
            "mock_call": True,
            "graded_at": datetime.utcnow().isoformat()
        }

        # Log usage if user_id provided
        if user_id and self.db:
            await self._log_llm_usage(
                user_id=user_id,
                feature_type="graded_assessment",
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                model_name=self.default_model,
                request_details={
                    "question_length": len(question),
                    "answer_length": len(student_answer),
                    "question_type": question_type
                },
                response_details={
                    "score": base_score,
                    "strengths_count": len(feedback["strengths"]),
                    "suggestions_count": len(feedback["specific_suggestions"])
                }
            )

        return result

    async def _real_grade_assessment(
        self,
        question: str,
        student_answer: str,
        rubric: str,
        question_type: str,
        user_id: int
    ) -> Dict[str, Any]:
        """Real assessment grading using OpenAI API"""

        prompt = f"""Grade this student answer:

Question: {question}

Student Answer: {student_answer}

Rubric: {rubric}

Provide your response as a JSON object with this exact structure:
{{
    "score": <integer 0-100>,
    "feedback": {{
        "strengths": [<list of 2-4 strengths>],
        "areas_for_improvement": [<list of 1-3 areas>],
        "specific_suggestions": [<list of 2-3 specific suggestions>]
    }},
    "rubric_scores": {{
        "clarity": <score 0-30>,
        "accuracy": <score 0-40>,
        "depth": <score 0-30>
    }}
}}

Be constructive, specific, and encouraging in your feedback."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert educational assessor providing detailed, constructive feedback on student answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Calculate token usage and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            cost_usd = self._calculate_cost(input_tokens, output_tokens)

            # Add metadata
            result["tokens_used"] = total_tokens
            result["cost_usd"] = round(cost_usd, 4)
            result["model_name"] = self.default_model
            result["mock_call"] = False
            result["graded_at"] = datetime.utcnow().isoformat()

            # Log usage
            if user_id and self.db:
                await self._log_llm_usage(
                    user_id=user_id,
                    feature_type="graded_assessment",
                    tokens_used=total_tokens,
                    cost_usd=cost_usd,
                    model_name=self.default_model,
                    request_details={
                        "question_length": len(question),
                        "answer_length": len(student_answer),
                        "question_type": question_type
                    },
                    response_details={
                        "score": result.get("score"),
                        "strengths_count": len(result.get("feedback", {}).get("strengths", [])),
                        "suggestions_count": len(result.get("feedback", {}).get("specific_suggestions", []))
                    }
                )

            return result

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Fall back to mock mode on error
            return await self._mock_grade_assessment(
                question=question,
                student_answer=student_answer,
                rubric=rubric,
                question_type=question_type,
                user_id=user_id
            )

    def _generate_strengths(self, question: str, answer: str) -> List[str]:
        """Generate realistic positive feedback"""
        possible_strengths = [
            "Good understanding of core concepts",
            "Clear and well-structured explanation",
            "Accurate use of terminology",
            "Relevant examples provided",
            "Logical flow of ideas",
            "Demonstrates critical thinking",
            "Strong opening statement",
            "Effective use of technical details",
            "Shows understanding of context",
            "Well-articulated key points"
        ]
        return random.sample(possible_strengths, k=random.randint(2, 4))

    def _generate_improvements(self, question: str, answer: str) -> List[str]:
        """Generate realistic areas for improvement"""
        possible_improvements = [
            "Could provide more specific examples",
            "Would benefit from deeper analysis",
            "Consider adding practical applications",
            "Could elaborate on key concepts",
            "Missing some technical details",
            "Could strengthen the conclusion",
            "Would benefit from more structure",
            "Consider counter-arguments",
            "Could connect to broader context",
            "Missing some important nuances"
        ]
        return random.sample(possible_improvements, k=random.randint(1, 3))

    def _generate_suggestions(self, question: str, answer: str) -> List[str]:
        """Generate specific improvement suggestions"""
        possible_suggestions = [
            "Add concrete examples to illustrate your points",
            "Include relevant equations or formulas",
            "Reference specific chapter sections",
            "Compare with alternative approaches",
            "Discuss practical implications",
            "Add a brief summary statement",
            "Use analogies to clarify complex ideas",
            "Include real-world use cases",
            "Mention recent developments in this area",
            "Connect to previous topics in the course"
        ]
        return random.sample(possible_suggestions, k=random.randint(2, 3))

    def _parse_rubric_scores(self, rubric: str, base_score: int) -> Dict[str, int]:
        """Parse rubric and generate category scores"""
        # Default rubric categories
        categories = ["clarity", "accuracy", "depth", "organization", "completeness"]

        # Generate scores that sum to approximately base_score
        scores = {}
        remaining = base_score

        for i, category in enumerate(categories[:-1]):
            # Allocate portion of score
            portion = random.randint(5, min(20, remaining - 5))
            scores[category] = portion
            remaining -= portion

        scores[categories[-1]] = remaining
        return scores

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate LLM API cost"""
        input_cost = (input_tokens / 1_000_000) * self.cost_per_million_input
        output_cost = (output_tokens / 1_000_000) * self.cost_per_million_output
        return input_cost + output_cost

    async def generate_learning_path(
        self,
        user_id: int,
        current_chapter_id: int,
        focus: str = "reinforce_weaknesses",
        include_completed: bool = True,
        learning_style: str = "mixed"
    ) -> Dict[str, Any]:
        """
        Generate adaptive learning path using LLM (or mock response)

        Args:
            user_id: User ID
            current_chapter_id: Current chapter ID
            focus: Learning focus ('reinforce_weaknesses', 'fastest_completion', 'deepest_understanding')
            include_completed: Whether to include completed chapters
            learning_style: Learning style preference ('visual', 'textual', 'mixed')

        Returns:
            Dict with personalized learning path recommendations
        """

        if self.mock_mode:
            return await self._mock_generate_learning_path(
                user_id=user_id,
                current_chapter_id=current_chapter_id,
                focus=focus,
                include_completed=include_completed,
                learning_style=learning_style
            )
        else:
            return await self._real_generate_learning_path(
                user_id=user_id,
                current_chapter_id=current_chapter_id,
                focus=focus,
                include_completed=include_completed,
                learning_style=learning_style
            )

    async def _mock_generate_learning_path(
        self,
        user_id: int,
        current_chapter_id: int,
        focus: str,
        include_completed: bool,
        learning_style: str
    ) -> Dict[str, Any]:
        """Mock learning path generation (Phase 2A)"""

        # Mock chapter data (will be fetched from database in real implementation)
        chapters = [
            {"id": 3, "title": "Transformer Architecture", "status": "completed", "quiz_score": 75},
            {"id": 5, "title": "Attention Mechanisms", "status": "in_progress", "completion": 75},
            {"id": 6, "title": "Large Language Models", "status": "not_started"},
        ]

        # Generate recommendations based on focus
        recommended_next = self._generate_recommendations(chapters, focus, current_chapter_id)

        # Identify knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(chapters, focus)

        # Generate study plan
        study_plan = self._generate_study_plan(chapters, focus)

        # Generate motivational message
        motivation = self._generate_motivation(chapters, focus)

        # Calculate token usage (simulated)
        input_tokens = 500  # User progress data
        output_tokens = 1500  # Learning path response
        total_tokens = input_tokens + output_tokens

        # Calculate cost
        cost_usd = self._calculate_cost(input_tokens, output_tokens)

        result = {
            "learning_path": {
                "current_status": f"Chapter {current_chapter_id} (75% complete)",
                "recommended_next": recommended_next,
                "knowledge_gaps": knowledge_gaps,
                "study_plan": study_plan,
                "motivation": motivation
            },
            "tokens_used": total_tokens,
            "cost_usd": round(cost_usd, 4),
            "model_name": self.default_model,
            "mock_call": True,
            "generated_at": datetime.utcnow().isoformat()
        }

        # Log usage if db available
        if self.db:
            await self._log_llm_usage(
                user_id=user_id,
                feature_type="learning_path",
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                model_name=self.default_model,
                request_details={
                    "current_chapter": current_chapter_id,
                    "focus": focus,
                    "learning_style": learning_style
                },
                response_details={
                    "recommendations_count": len(recommended_next),
                    "gaps_identified": len(knowledge_gaps)
                }
            )

        return result

    async def _real_generate_learning_path(
        self,
        user_id: int,
        current_chapter_id: int,
        focus: str,
        include_completed: bool,
        learning_style: str
    ) -> Dict[str, Any]:
        """Real learning path generation using OpenAI API"""

        # Get user's learning data from database
        user_progress = await self._get_user_progress(user_id)

        prompt = f"""Analyze this student's learning data and generate personalized recommendations:

Student Progress Data:
{json.dumps(user_progress, indent=2)}

Current Chapter: {current_chapter_id}
Focus: {focus}
Learning Style: {learning_style}

Provide your response as a JSON object with this exact structure:
{{
    "learning_path": {{
        "current_status": "<brief status summary>",
        "recommended_next": [
            {{
                "chapter": <integer>,
                "title": "<chapter title>",
                "reason": "<why this chapter is recommended>",
                "priority": "<high|medium|low>",
                "estimated_difficulty": "<easy|medium|hard>"
            }}
        ],
        "knowledge_gaps": [
            {{
                "topic": "<topic name>",
                "gap_severity": "<minor|moderate|significant>",
                "recommended_resources": ["<resource 1>", "<resource 2>"]
            }}
        ],
        "study_plan": {{
            "this_week": ["<task 1>", "<task 2>", "<task 3>"],
            "next_week": ["<task 1>", "<task 2>", "<task 3>"]
        }},
        "motivation": "<motivational message>"
    }}
}}

Consider:
- Prerequisite relationships between chapters
- Weak areas that need reinforcement (if focus is reinforce_weaknesses)
- Optimal sequence for completion (if focus is fastest_completion)
- Deep understanding approach (if focus is deepest_understanding)
- Learning speed and preferences from their data"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "You are an expert educational advisor creating personalized learning paths for students studying Generative AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Calculate token usage and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            cost_usd = self._calculate_cost(input_tokens, output_tokens)

            # Add metadata
            result["tokens_used"] = total_tokens
            result["cost_usd"] = round(cost_usd, 4)
            result["model_name"] = self.default_model
            result["mock_call"] = False
            result["generated_at"] = datetime.utcnow().isoformat()

            # Log usage
            if self.db:
                await self._log_llm_usage(
                    user_id=user_id,
                    feature_type="learning_path",
                    tokens_used=total_tokens,
                    cost_usd=cost_usd,
                    model_name=self.default_model,
                    request_details={
                        "current_chapter": current_chapter_id,
                        "focus": focus,
                        "learning_style": learning_style
                    },
                    response_details={
                        "recommendations_count": len(result.get("learning_path", {}).get("recommended_next", [])),
                        "gaps_identified": len(result.get("learning_path", {}).get("knowledge_gaps", []))
                    }
                )

            return result

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Fall back to mock mode on error
            return await self._mock_generate_learning_path(
                user_id=user_id,
                current_chapter_id=current_chapter_id,
                focus=focus,
                include_completed=include_completed,
                learning_style=learning_style
            )

    async def _get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get user's learning progress from database"""
        # TODO: Implement database query to get real user progress
        # For now, return mock data
        return {
            "completed_chapters": [1, 2, 3, 4],
            "current_chapter": 5,
            "quiz_scores": {
                1: 85,
                2: 78,
                3: 72,
                4: 88,
                5: 80
            },
            "time_spent_hours": {
                1: 2.5,
                2: 3.0,
                3: 4.0,
                4: 2.0,
                5: 1.5
            },
            "learning_streak_days": 7,
            "last_activity": datetime.utcnow().isoformat()
        }

    def _generate_recommendations(
        self,
        chapters: List[Dict],
        focus: str,
        current_chapter_id: int
    ) -> List[Dict[str, Any]]:
        """Generate chapter recommendations based on focus"""

        recommendations = []

        if focus == "reinforce_weaknesses":
            recommendations.append({
                "chapter": 3,
                "title": "Transformer Architecture (Review)",
                "reason": "Your quiz score here was lower than other chapters",
                "priority": "medium",
                "estimated_difficulty": "easy (review)"
            })
            recommendations.append({
                "chapter": 6,
                "title": "Large Language Models",
                "reason": "Builds on Chapter 5 foundation, solidifies understanding",
                "priority": "high",
                "estimated_difficulty": "medium"
            })

        elif focus == "fastest_completion":
            recommendations.append({
                "chapter": 6,
                "title": "Large Language Models",
                "reason": "Next chapter in sequence",
                "priority": "high",
                "estimated_difficulty": "medium"
            })
            recommendations.append({
                "chapter": 7,
                "title": "Prompt Engineering",
                "reason": "Continues learning sequence efficiently",
                "priority": "medium",
                "estimated_difficulty": "easy"
            })

        else:  # deepest_understanding
            recommendations.append({
                "chapter": 5,
                "title": "Complete Attention Mechanisms",
                "reason": "Finish current chapter first for strong foundation",
                "priority": "high",
                "estimated_difficulty": "medium"
            })
            recommendations.append({
                "chapter": 3,
                "title": "Transformer Architecture (Deep Dive)",
                "reason": "Revisit with more depth for stronger fundamentals",
                "priority": "medium",
                "estimated_difficulty": "medium"
            })

        return recommendations

    def _identify_knowledge_gaps(
        self,
        chapters: List[Dict],
        focus: str
    ) -> List[Dict[str, Any]]:
        """Identify knowledge gaps based on focus"""

        gaps = []

        if focus == "reinforce_weaknesses":
            gaps.append({
                "topic": "Multi-head attention",
                "gap_severity": "moderate",
                "recommended_resources": ["Chapter 5, Section 3", "Practice Quiz 5.3"]
            })
            gaps.append({
                "topic": "Positional encoding",
                "gap_severity": "minor",
                "recommended_resources": ["Chapter 5, Section 2"]
            })

        return gaps

    def _generate_study_plan(
        self,
        chapters: List[Dict],
        focus: str
    ) -> Dict[str, List[str]]:
        """Generate weekly study plan"""

        return {
            "this_week": [
                "Complete Chapter 5 (remaining 25%)",
                "Review Chapter 3, Section 4 (positional encoding)",
                "Take Chapter 5 quiz",
                "Review feedback on recent assessments"
            ],
            "next_week": [
                "Start Chapter 6: Large Language Models",
                "Complete Chapter 6 quiz",
                "Review synthesis: Chapters 3-6",
                "Identify next areas for focus"
            ]
        }

    def _generate_motivation(
        self,
        chapters: List[Dict],
        focus: str
    ) -> str:
        """Generate motivational message"""

        motivations = [
            "You're making great progress! Focusing on these areas will solidify your understanding.",
            "Your dedication shows! Keep up the excellent work and you'll master these topics.",
            "Great job so far! These targeted improvements will take you to the next level.",
            "You're on track for success! Focusing here will pay off in your learning journey."
        ]

        return random.choice(motivations)

    async def _log_llm_usage(
        self,
        user_id: int,
        feature_type: str,
        tokens_used: int,
        cost_usd: float,
        model_name: str,
        request_details: Dict[str, Any] = None,
        response_details: Dict[str, Any] = None
    ):
        """Log LLM usage to database for cost tracking"""

        if not self.db:
            return

        try:
            from app.models.llm_usage import LLMUsageLog

            log_entry = LLMUsageLog(
                user_id=user_id,
                feature_type=feature_type,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                model_name=model_name,
                request_details=json.dumps(request_details) if request_details else None,
                response_details=json.dumps(response_details) if response_details else None,
                mock_call=self.mock_mode
            )

            self.db.add(log_entry)
            self.db.commit()

        except Exception as e:
            # Log error but don't fail the request
            print(f"Error logging LLM usage: {e}")

    def get_monthly_usage(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Get monthly LLM usage summary for a user"""

        if not self.db:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "assessments_count": 0,
                "learning_paths_count": 0
            }

        # Query database for monthly usage
        # TODO: Implement database query
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "assessments_count": 0,
            "learning_paths_count": 0
        }
