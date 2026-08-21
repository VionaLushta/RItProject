import { useEffect, useMemo, useState } from "react";
import { QUICK_ACTIONS, DIFFICULTY_OPTIONS, SUMMARY_STYLE_OPTIONS, QUIZ_COUNT_OPTIONS } from "./appData";
import {
  ActionButton,
  EmptyState,
  Field,
  InputField,
  MetricCard,
  QuickActionCard,
  QuizQuestionCard,
  SelectField,
  StatusBanner,
  TextAreaField,
} from "./components";
import {
  ApiError,
  askQuestion,
  explainTopic,
  generateQuiz,
  getHistory,
  getStatistics,
  submitQuiz,
  summarizeText,
} from "./services/api";

function formatAverageScore(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return "0.0%";
  }
  return `${numeric.toFixed(1)}%`;
}

function buildRecentActivity(history) {
  const questionEntries = history.questions.map((item, index) => ({
    id: `question-${index}`,
    type: "Question",
    title: item.question,
    description: item.answer,
  }));

  const quizEntries = history.quizzes.map((item, index) => ({
    id: `quiz-${index}`,
    type: "Quiz",
    title: `${item.topic} - ${item.difficulty}`,
    description: `${item.correct_answers}/${item.total_questions} correct, ${item.score_percentage}%`,
  }));

  return [...questionEntries, ...quizEntries].slice(-4).reverse();
}

function LoadingNotice({ text }) {
  return (
    <StatusBanner
      tone="info"
      icon="spark"
      title={text}
      message="Please wait while CampusMate loads your study data."
    />
  );
}

export function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [statsResponse, historyResponse] = await Promise.all([getStatistics(), getHistory()]);
        if (!active) {
          return;
        }
        setStats(statsResponse);
        setHistory(historyResponse);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof ApiError ? err.message : "CampusMate couldn't load the dashboard right now.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  const recentActivity = useMemo(() => (history ? buildRecentActivity(history) : []), [history]);

  return (
    <div className="dashboard">
      <section className="dashboard-hero">
        <div className="dashboard-hero__copy">
          <p className="eyebrow">CampusMate AI</p>
          <h2>Welcome to CampusMate AI</h2>
          <p>Your study tools, organized in one place.</p>
        </div>
      </section>

      {loading ? <LoadingNotice text="Loading dashboard data..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Dashboard unavailable" message={error} /> : null}

      <section className="section-block">
        <div className="section-block__header">
          <h3>Quick Actions</h3>
          <p>Jump straight into the next thing you want to study.</p>
        </div>
        <div className="quick-grid">
          {QUICK_ACTIONS.map((item) => (
            <QuickActionCard key={item.path} {...item} />
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-block__header">
          <h3>Study Overview</h3>
          <p>Real backend values update as you use CampusMate.</p>
        </div>
        <div className="stats-grid">
          <MetricCard
            label="Questions Asked"
            value={stats ? stats.questions_asked : "0"}
            hint={loading ? "Loading..." : "From backend statistics"}
            icon="ask"
          />
          <MetricCard
            label="Quizzes Completed"
            value={stats ? stats.quizzes_completed : "0"}
            hint={loading ? "Loading..." : "From backend statistics"}
            icon="quiz"
          />
          <MetricCard
            label="Correct Answers"
            value={stats ? stats.correct_answers : "0"}
            hint={loading ? "Loading..." : "From backend statistics"}
            icon="statistics"
          />
          <MetricCard
            label="Average Score"
            value={stats ? formatAverageScore(stats.average_quiz_score) : "0.0%"}
            hint={loading ? "Loading..." : "From backend statistics"}
            icon="chart"
          />
        </div>
      </section>

      <section className="section-block">
        <div className="section-block__header">
          <h3>Recent Activity</h3>
          <p>Most recent questions and quiz results from your history.</p>
        </div>
        {!loading && recentActivity.length === 0 ? (
          <EmptyState
            title="No study activity yet."
            description="Your recent questions and quizzes will appear here."
          />
        ) : null}
        {recentActivity.length > 0 ? (
          <div className="history-cards">
            {recentActivity.map((item) => (
              <article className="history-card" key={item.id}>
                <div className="history-card__meta">{item.type}</div>
                <h4>{item.title}</h4>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}

export function AskAiPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setValidationError("Please enter a question before asking CampusMate.");
      return;
    }

    setLoading(true);
    setError("");
    setValidationError("");

    try {
      const response = await askQuestion(trimmedQuestion);
      setAnswer(response.answer);
    } catch (err) {
      setAnswer("");
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">Ask AI</p>
        <h2>Ask CampusMate a study question.</h2>
        <p>Get a clear answer from the existing Python backend.</p>
      </div>

      <form className="tool-form" onSubmit={handleSubmit}>
        <Field
          label="Question"
          htmlFor="ask-question"
          hint="Write a specific question about a topic you are studying."
          error={validationError}
          required
        >
          <TextAreaField
            id="ask-question"
            rows={6}
            placeholder="What is the difference between TCP and UDP?"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
        </Field>

        <div className="form-actions">
          <ActionButton type="submit" disabled={loading}>
            {loading ? "Asking CampusMate..." : "Ask CampusMate"}
          </ActionButton>
        </div>
      </form>

      {loading ? <LoadingNotice text="Asking CampusMate..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {answer ? (
        <section className="result-panel">
          <div className="result-panel__header">
            <h3>Answer</h3>
          </div>
          <p className="result-panel__body">{answer}</p>
        </section>
      ) : null}
    </section>
  );
}

export function ExplainTopicPage() {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedTopic = topic.trim();

    if (!trimmedTopic) {
      setValidationError("Please enter a topic to explain.");
      return;
    }

    setLoading(true);
    setError("");
    setValidationError("");

    try {
      const response = await explainTopic(trimmedTopic, difficulty);
      setExplanation(response.explanation);
    } catch (err) {
      setExplanation("");
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">Explain Topic</p>
        <h2>Explore a topic at the right level.</h2>
        <p>Choose a difficulty and let the backend produce the explanation.</p>
      </div>

      <form className="tool-form" onSubmit={handleSubmit}>
        <Field
          label="Topic"
          htmlFor="explain-topic"
          hint="Enter the topic you want CampusMate to explain."
          error={validationError}
          required
        >
          <InputField
            id="explain-topic"
            type="text"
            placeholder="Photosynthesis"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />
        </Field>

        <Field label="Difficulty" htmlFor="explain-difficulty" hint="Select the level that fits your study needs." required>
          <SelectField id="explain-difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
            {DIFFICULTY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </SelectField>
        </Field>

        <div className="form-actions">
          <ActionButton type="submit" disabled={loading}>
            {loading ? "Creating explanation..." : "Explain Topic"}
          </ActionButton>
        </div>
      </form>

      {loading ? <LoadingNotice text="Creating explanation..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {explanation ? (
        <section className="result-panel">
          <div className="result-panel__header">
            <h3>Explanation</h3>
          </div>
          <p className="result-panel__body">{explanation}</p>
        </section>
      ) : null}
    </section>
  );
}

export function SummarizePage() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState("short");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedText = text.trim();

    if (!trimmedText) {
      setValidationError("Please paste or type text to summarize.");
      return;
    }

    setLoading(true);
    setError("");
    setValidationError("");

    try {
      const response = await summarizeText(trimmedText, style);
      setSummary(response.summary);
    } catch (err) {
      setSummary("");
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">Summarize Text</p>
        <h2>Turn long material into useful study notes.</h2>
        <p>Choose a summary style and send the text to the backend.</p>
      </div>

      <form className="tool-form" onSubmit={handleSubmit}>
        <Field
          label="Source text"
          htmlFor="summary-text"
          hint="Paste notes, an article, or a passage you want summarized."
          error={validationError}
          required
        >
          <TextAreaField
            id="summary-text"
            rows={10}
            placeholder="Paste the text you want summarized here..."
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
        </Field>

        <Field label="Summary style" htmlFor="summary-style" hint="Pick the summary format that helps you study best." required>
          <SelectField id="summary-style" value={style} onChange={(event) => setStyle(event.target.value)}>
            {SUMMARY_STYLE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </SelectField>
        </Field>

        <div className="form-actions">
          <ActionButton type="submit" disabled={loading}>
            {loading ? "Summarizing..." : "Summarize Text"}
          </ActionButton>
        </div>
      </form>

      {loading ? <LoadingNotice text="Summarizing..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {summary ? (
        <section className="result-panel">
          <div className="result-panel__header">
            <h3>Summary</h3>
          </div>
          <p className="result-panel__body result-panel__body--preserve">{summary}</p>
        </section>
      ) : null}
    </section>
  );
}

export function QuizPage() {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("beginner");
  const [questionCount, setQuestionCount] = useState("5");
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [scoreResult, setScoreResult] = useState(null);
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");

  const allAnswered = quiz ? answers.filter(Boolean).length === quiz.questions.length : false;

  async function handleGenerate(event) {
    event.preventDefault();
    const trimmedTopic = topic.trim();
    const parsedCount = Number.parseInt(questionCount, 10);

    if (!trimmedTopic) {
      setValidationError("Please enter a topic for the quiz.");
      return;
    }

    if (!Number.isInteger(parsedCount) || parsedCount < 1 || parsedCount > 10) {
      setValidationError("Question count must be between 1 and 10.");
      return;
    }

    setLoadingGenerate(true);
    setError("");
    setValidationError("");
    setScoreResult(null);

    try {
      const response = await generateQuiz(trimmedTopic, difficulty, parsedCount);
      setQuiz(response.quiz);
      setAnswers(Array(response.quiz.questions.length).fill(""));
    } catch (err) {
      setQuiz(null);
      setAnswers([]);
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoadingGenerate(false);
    }
  }

  async function handleSubmitQuiz() {
    if (!quiz) {
      return;
    }

    if (answers.some((answer) => !answer)) {
      setValidationError("Please answer every question before submitting the quiz.");
      return;
    }

    setLoadingSubmit(true);
    setError("");
    setValidationError("");

    try {
      const response = await submitQuiz(quiz, answers);
      setScoreResult(response.result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoadingSubmit(false);
    }
  }

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">Quiz</p>
        <h2>Generate a practice quiz and submit your answers.</h2>
        <p>Quiz scoring happens in Python. Answers stay hidden until you submit.</p>
      </div>

      <form className="tool-form" onSubmit={handleGenerate}>
        <Field label="Topic" htmlFor="quiz-topic" hint="Enter the topic you want to test yourself on." error={validationError} required>
          <InputField
            id="quiz-topic"
            type="text"
            placeholder="Photosynthesis"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />
        </Field>

        <Field label="Difficulty" htmlFor="quiz-difficulty" required>
          <SelectField id="quiz-difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
            {DIFFICULTY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </SelectField>
        </Field>

        <Field label="Number of questions" htmlFor="quiz-count" hint="Choose between 1 and 10." required>
          <SelectField id="quiz-count" value={questionCount} onChange={(event) => setQuestionCount(event.target.value)}>
            {QUIZ_COUNT_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </SelectField>
        </Field>

        <div className="form-actions">
          <ActionButton type="submit" disabled={loadingGenerate}>
            {loadingGenerate ? "Generating quiz..." : "Generate Quiz"}
          </ActionButton>
        </div>
      </form>

      {loadingGenerate ? <LoadingNotice text="Generating quiz..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {quiz ? (
        <section className="result-panel">
          <div className="result-panel__header result-panel__header--stack">
            <div>
              <h3>{quiz.topic} Quiz</h3>
              <p>{quiz.difficulty} level, {quiz.questions.length} questions</p>
            </div>
            <ActionButton type="button" variant="secondary" onClick={handleSubmitQuiz} disabled={loadingSubmit || !allAnswered}>
              {loadingSubmit ? "Checking answers..." : "Submit Quiz"}
            </ActionButton>
          </div>

          <div className="quiz-list">
            {quiz.questions.map((item, index) => (
              <QuizQuestionCard
                key={`${quiz.topic}-${index}`}
                index={index + 1}
                question={item}
                selectedAnswer={answers[index]}
                onChange={(value) => {
                  const nextAnswers = [...answers];
                  nextAnswers[index] = value;
                  setAnswers(nextAnswers);
                }}
                disabled={loadingSubmit}
              />
            ))}
          </div>
        </section>
      ) : null}

      {validationError && quiz ? (
        <StatusBanner tone="error" icon="alert" title="Complete the quiz" message={validationError} />
      ) : null}

      {scoreResult ? (
        <section className="result-panel result-panel--score">
          <div className="result-panel__header">
            <h3>Quiz Result</h3>
          </div>
          <div className="score-grid">
            <MetricCard label="Score" value={`${scoreResult.score_percentage}%`} hint="Backend calculated" icon="chart" />
            <MetricCard label="Correct" value={scoreResult.correct_answers} hint="Backend calculated" icon="check" />
            <MetricCard label="Incorrect" value={scoreResult.incorrect_answers} hint="Backend calculated" icon="alert" />
            <MetricCard label="Total" value={scoreResult.total_questions} hint="Backend calculated" icon="quiz" />
          </div>
          {Array.isArray(scoreResult.feedback) && scoreResult.feedback.length > 0 ? (
            <div className="feedback-list">
              {scoreResult.feedback.map((item) => (
                <article className={`feedback-item ${item.is_correct ? "is-correct" : "is-incorrect"}`} key={item.question_number}>
                  <div className="feedback-item__meta">Question {item.question_number}</div>
                  <p>{item.is_correct ? "Correct" : "Incorrect"}</p>
                  <div className="feedback-item__details">
                    <span>Selected: {item.selected_answer}</span>
                    <span>Correct: {item.correct_answer}</span>
                  </div>
                </article>
              ))}
            </div>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}

export function HistoryPage() {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadHistory() {
      setLoading(true);
      setError("");

      try {
        const response = await getHistory();
        if (active) {
          setHistory(response);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof ApiError ? err.message : "CampusMate couldn't load history right now.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      active = false;
    };
  }, []);

  const hasActivity = history && (history.questions.length > 0 || history.quizzes.length > 0);

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">History</p>
        <h2>Review your stored questions and quizzes.</h2>
        <p>Everything shown here comes from the Python backend history store.</p>
      </div>

      {loading ? <LoadingNotice text="Loading history..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="History unavailable" message={error} /> : null}

      {!loading && !error && !hasActivity ? (
        <EmptyState
          title="No study history yet."
          description="Ask a question or complete a quiz and your activity will appear here."
        />
      ) : null}

      {history && history.questions.length > 0 ? (
        <section className="section-block">
          <div className="section-block__header">
            <h3>Questions</h3>
            <p>Original question and answer saved by the backend.</p>
          </div>
          <div className="history-list">
            {history.questions.map((item, index) => (
              <article className="history-entry" key={`${item.question}-${index}`}>
                <div className="history-entry__type">Question</div>
                <h4>{item.question}</h4>
                <p>{item.answer}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {history && history.quizzes.length > 0 ? (
        <section className="section-block">
          <div className="section-block__header">
            <h3>Completed Quizzes</h3>
            <p>Persisted quiz results from the backend storage.</p>
          </div>
          <div className="history-list">
            {history.quizzes.map((item, index) => (
              <article className="history-entry" key={`${item.topic}-${index}`}>
                <div className="history-entry__type">Quiz</div>
                <h4>{item.topic}</h4>
                <p>
                  Difficulty: {item.difficulty} | Score: {item.score_percentage}% | Correct: {item.correct_answers}/
                  {item.total_questions}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </section>
  );
}

export function StatisticsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadStatistics() {
      setLoading(true);
      setError("");

      try {
        const response = await getStatistics();
        if (active) {
          setStats(response);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof ApiError ? err.message : "CampusMate couldn't load statistics right now.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadStatistics();

    return () => {
      active = false;
    };
  }, []);

  const accuracy = useMemo(() => {
    if (!stats) {
      return 0;
    }

    const totalAnswered = Number(stats.correct_answers || 0) + Number(stats.incorrect_answers || 0);
    if (!totalAnswered) {
      return 0;
    }

    return Math.round((Number(stats.correct_answers || 0) / totalAnswered) * 100);
  }, [stats]);

  return (
    <section className="tool-page">
      <div className="tool-page__intro">
        <p className="eyebrow">Statistics</p>
        <h2>Track your real study activity.</h2>
        <p>These values are loaded directly from the backend statistics store.</p>
      </div>

      {loading ? <LoadingNotice text="Loading statistics..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Statistics unavailable" message={error} /> : null}

      {stats ? (
        <>
          <div className="stats-grid">
            <MetricCard label="Questions Asked" value={stats.questions_asked} hint="From backend statistics" icon="ask" />
            <MetricCard label="Quizzes Completed" value={stats.quizzes_completed} hint="From backend statistics" icon="quiz" />
            <MetricCard label="Correct Answers" value={stats.correct_answers} hint="From backend statistics" icon="check" />
            <MetricCard label="Incorrect Answers" value={stats.incorrect_answers} hint="From backend statistics" icon="alert" />
          </div>

          <section className="result-panel">
            <div className="result-panel__header">
              <h3>Average Quiz Score</h3>
            </div>
            <div className="score-meter" aria-label={`Average quiz score ${formatAverageScore(stats.average_quiz_score)}`}>
              <div className="score-meter__value">{formatAverageScore(stats.average_quiz_score)}</div>
              <div className="score-meter__track">
                <div className="score-meter__fill" style={{ width: `${Math.max(0, Math.min(100, Number(stats.average_quiz_score) || 0))}%` }} />
              </div>
              <p className="score-meter__caption">Accuracy estimate: {accuracy}%</p>
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}

export function PlaceholderPage({ title, description }) {
  return (
    <section className="placeholder-page">
      <div className="placeholder-card">
        <p className="eyebrow">{title}</p>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </section>
  );
}
