import { useSession } from "@gadgetinc/react";
import { useDisplayMode, useRequestDisplayMode } from "@gadgetinc/react-chatgpt-apps";
import { Button } from "@openai/apps-sdk-ui/components/Button";
import { ChevronLeft, ChevronRight, Expand, BookOpen, Target, Flame, Trophy } from "lucide-react";
import { Link, MemoryRouter, Route, Routes, useNavigate } from "react-router";
import { useEffect, useState } from "react";

const HelloGadgetRouter = () => {
  const displayMode = useDisplayMode();
  return (
    <div className={`p-6 max-w-2xl mx-auto ${displayMode === "fullscreen" ? "h-screen" : ""}`}>
      <div className="w-full flex">
        <FullscreenButton />
      </div>
      <MemoryRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chapters" element={<Chapters />} />
          <Route path="/chapter/:id" element={<ChapterDetail />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </MemoryRouter>
    </div>
  );
};

function FullscreenButton() {
  const requestDisplayMode = useRequestDisplayMode();
  const displayMode = useDisplayMode();

  if (displayMode === "fullscreen" || !requestDisplayMode) {
    return null;
  }

  return (
    <Button
      color="secondary"
      variant="soft"
      aria-label="Enter fullscreen"
      className="rounded-full size-10 ml-auto"
      onClick={() => requestDisplayMode("fullscreen")}
    >
      <Expand />
    </Button>
  );
}

// Backend API URL
const API_URL = "https://course-companion-fte.fly.dev";

// Home page with navigation options
function Home() {
  return (
    <div>
      <div className="text-center flex flex-col justify-center min-h-[200px]">
        <div className="flex items-center justify-center mb-6">
          <BookOpen className="w-12 h-12 text-blue-500 mr-3" />
          <h1 className="text-2xl font-bold tracking-tight">Course Companion FTE</h1>
        </div>
        <p className="text-muted-foreground mb-6">Master Generative AI Fundamentals</p>

        <div className="flex flex-col gap-3">
          <Link to="/chapters">
            <Button color="primary" className="w-full">
              <BookOpen className="w-4 h-4 mr-2" />
              Browse Chapters
            </Button>
          </Link>
          <Link to="/progress">
            <Button color="primary" variant="outline" className="w-full">
              <Target className="w-4 h-4 mr-2" />
              View Progress
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex gap-2 mt-4">
        <Link to="/about" className="ml-auto">
          <Button color="primary" variant="ghost">
            About
            <ChevronRight />
          </Button>
        </Link>
      </div>
    </div>
  );
}

// Chapters page
function Chapters() {
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/chapters`)
      .then(res => res.json())
      .then(data => {
        setChapters(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching chapters:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Course Chapters</h2>
        <Link to="/">
          <Button color="primary" variant="ghost" size="sm">
            <ChevronLeft />
            Home
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading chapters...</div>
      ) : (
        <div className="space-y-3">
          {chapters.map((chapter, index) => (
            <Link key={chapter.id} to={`/chapter/${chapter.id}`}>
              <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-muted-foreground">Chapter {index + 1}</span>
                      {chapter.is_free && (
                        <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded-full">Free</span>
                      )}
                    </div>
                    <h3 className="font-semibold mb-1">{chapter.title}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">{chapter.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-muted-foreground ml-2" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

// Chapter detail page
function ChapterDetail() {
  const [chapter, setChapter] = useState(null);
  const [loading, setLoading] = useState(true);

  // Extract chapter ID from current location
  useEffect(() => {
    const path = window.location.pathname;
    const id = path.split('/').pop();

    if (id && id !== 'chapter') {
      fetch(`${API_URL}/api/v1/chapters/${id}`)
        .then(res => res.json())
        .then(data => {
          setChapter(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching chapter:", err);
          setLoading(false);
        });
    }
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading chapter...</div>;
  }

  if (!chapter) {
    return (
      <div>
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4">Chapter not found</p>
          <Link to="/chapters">
            <Button color="primary">Back to Chapters</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <Link to="/chapters">
          <Button color="primary" variant="ghost" size="sm">
            <ChevronLeft />
            Back to Chapters
          </Button>
        </Link>
      </div>

      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">{chapter.title}</h2>
          <p className="text-muted-foreground">{chapter.description}</p>
        </div>

        {chapter.sections && chapter.sections.length > 0 && (
          <div>
            <h3 className="font-semibold mb-3">Sections</h3>
            <div className="space-y-2">
              {chapter.sections.map((section, index) => (
                <div key={section.id} className="p-3 border rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-sm">
                        {index + 1}. {section.title}
                      </h4>
                      {section.content && (
                        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                          {section.content.substring(0, 150)}...
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Progress page
function Progress() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/progress`)
      .then(res => res.json())
      .then(data => {
        setProgress(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching progress:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Learning Progress</h2>
        <Link to="/">
          <Button color="primary" variant="ghost" size="sm">
            <ChevronLeft />
            Home
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading progress...</div>
      ) : progress ? (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg text-center">
              <Flame className="w-6 h-6 text-orange-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">{progress.current_streak || 0}</div>
              <div className="text-sm text-muted-foreground">Day Streak</div>
            </div>
            <div className="p-4 border rounded-lg text-center">
              <Trophy className="w-6 h-6 text-yellow-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">{progress.completion_percentage || 0}%</div>
              <div className="text-sm text-muted-foreground">Complete</div>
            </div>
            <div className="p-4 border rounded-lg text-center">
              <BookOpen className="w-6 h-6 text-blue-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">{progress.chapters_completed || 0}/{progress.total_chapters || 6}</div>
              <div className="text-sm text-muted-foreground">Chapters</div>
            </div>
          </div>

          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold mb-2">Total Active Days</h3>
            <div className="text-3xl font-bold">{progress.total_active_days || 0}</div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4">No progress data available</p>
          <p className="text-sm text-muted-foreground">Sign in to track your learning progress</p>
        </div>
      )}
    </div>
  );
}

// About page
function About() {
  return (
    <div>
      <div className="flex flex-col gap-3 px-8 py-6">
        <h1 className="text-xl font-semibold tracking-tight">Course Companion FTE</h1>

        <p>
          Your AI-powered learning companion for mastering Generative AI fundamentals.
          Access comprehensive course content, track your progress, and engage with interactive quizzes.
        </p>

        <div className="mt-4 space-y-2">
          <h3 className="font-semibold">Features:</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            <li>6 comprehensive chapters covering AI fundamentals</li>
            <li>Interactive quizzes to test your knowledge</li>
            <li>Progress tracking with streaks and milestones</li>
            <li>Adaptive learning paths powered by AI</li>
            <li>Integration with ChatGPT for seamless learning</li>
          </ul>
        </div>

        <div className="mt-4 p-3 bg-muted rounded-lg">
          <p className="text-sm">
            <strong>Access the full course at:</strong><br />
            <a href="https://course-companion-web.fly.dev" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
              course-companion-web.fly.dev
            </a>
          </p>
        </div>
      </div>

      <Link to="/">
        <Button color="primary" variant="ghost">
          <ChevronLeft />
          Home
        </Button>
      </Link>
    </div>
  );
}

export default HelloGadgetRouter;