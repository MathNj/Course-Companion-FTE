#!/bin/bash
# Verification script to check if system is ready for ChatGPT testing

echo "============================================"
echo "Course Companion FTE - Readiness Check"
echo "============================================"
echo ""

# Check 1: Docker containers
echo "✓ Checking Docker containers..."
if docker-compose ps | grep -q "healthy"; then
    echo "  ✅ Docker containers are running"
else
    echo "  ❌ Docker containers not running"
    echo "     Run: docker-compose up -d"
    exit 1
fi
echo ""

# Check 2: Backend health
echo "✓ Checking backend health..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "  ✅ Backend is healthy"
else
    echo "  ❌ Backend not responding"
    echo "     Check: docker-compose logs backend"
    exit 1
fi
echo ""

# Check 3: Database connectivity
echo "✓ Checking database..."
if docker-compose exec -T postgres pg_isready -U course_companion > /dev/null 2>&1; then
    echo "  ✅ Database is ready"
else
    echo "  ❌ Database not ready"
    exit 1
fi
echo ""

# Check 4: Redis connectivity
echo "✓ Checking Redis..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "  ✅ Redis is ready"
else
    echo "  ❌ Redis not ready"
    exit 1
fi
echo ""

# Check 5: API endpoints
echo "✓ Checking API endpoints..."
if curl -s http://localhost:8001/api/v1/chapters | grep -q "chapter-1"; then
    echo "  ✅ Chapters endpoint working"
else
    echo "  ❌ Chapters endpoint failed"
    exit 1
fi
echo ""

# Check 6: OpenAPI schema
echo "✓ Checking OpenAPI schema..."
if curl -s http://localhost:8001/api/openapi.json | grep -q "get_chapters"; then
    echo "  ✅ OpenAPI schema available"
else
    echo "  ❌ OpenAPI schema not found"
    exit 1
fi
echo ""

# Check 7: Content files
echo "✓ Checking content files..."
CHAPTER_COUNT=$(find backend/content/chapters -name "chapter-*.json" 2>/dev/null | wc -l)
QUIZ_COUNT=$(find backend/content/quizzes -name "chapter-*-quiz.json" 2>/dev/null | wc -l)

if [ "$CHAPTER_COUNT" -eq 6 ] && [ "$QUIZ_COUNT" -eq 6 ]; then
    echo "  ✅ All content files present (6 chapters, 6 quizzes)"
else
    echo "  ⚠️  Content files: $CHAPTER_COUNT chapters, $QUIZ_COUNT quizzes"
fi
echo ""

# Check 8: ChatGPT app files
echo "✓ Checking ChatGPT app files..."
if [ -f "chatgpt-app/instructions.md" ] && [ -f "chatgpt-app/openapi.yaml" ]; then
    echo "  ✅ ChatGPT configuration files present"
else
    echo "  ❌ ChatGPT files missing"
    exit 1
fi
echo ""

# Summary
echo "============================================"
echo "✅ ALL CHECKS PASSED!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Install ngrok: https://ngrok.com/download"
echo "2. Run: ngrok http 8001"
echo "3. Copy the https://....ngrok-free.app URL"
echo "4. Follow TESTING-GUIDE.md to create Custom GPT"
echo ""
echo "Backend URL: http://localhost:8001"
echo "OpenAPI Schema: http://localhost:8001/api/openapi.json"
echo "Health Check: http://localhost:8001/health"
echo ""
echo "Happy testing! 🚀"
