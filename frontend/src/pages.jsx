import { useEffect, useRef, useState } from "react";
import { QUICK_ACTIONS, DIFFICULTY_OPTIONS, SUMMARY_STYLE_OPTIONS, QUIZ_COUNT_OPTIONS } from "./appData";
import { MarkdownResponse } from "./markdownRenderer";
import {
  ActionButton,
  Field,
  Icon,
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
  askQuestionStream,
  deleteHistoryItem,
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

function formatInteractionDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function previewText(value, maxLength = 150) {
  if (!value) {
    return "No preview available yet.";
  }

  const cleaned = String(value)
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/[#*_`>[\]()]/g, "")
    .replace(/\s+/g, " ")
    .trim();

  if (cleaned.length <= maxLength) {
    return cleaned;
  }

  return `${cleaned.slice(0, maxLength).trim()}...`;
}

function LoadingNotice({ text }) {
  return (
    <StatusBanner
      tone="info"
      icon="spark"
      title={text}
      message="Please wait while CampusMate completes this step."
    />
  );
}

export function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const statsResponse = await getStatistics();
        if (!active) {
          return;
        }
        setStats(statsResponse);
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

  return (
    <div className="dashboard">
      <section className="dashboard-hero">
        <div className="dashboard-hero__copy">
          <div className="ask-chat__welcome-icon dashboard-hero__icon" aria-hidden="true">
            <Icon name="dashboard" />
          </div>
          <p className="eyebrow">CAMPUSMATE AI</p>
          <h2>Welcome to CampusMate AI</h2>
          <p>Choose a study tool, ask questions, generate quizzes, and track your progress in one place.</p>
        </div>
        <div className="dashboard-hero__visual" aria-hidden="true">
          <div className="dashboard-hero__mesh" />
          <div className="dashboard-hero__panel dashboard-hero__panel--device">
            <div className="dashboard-hero__panel-header">
              <span className="dashboard-hero__pill dashboard-hero__pill--blue">AI</span>
              <span className="dashboard-hero__pill dashboard-hero__pill--red">Study</span>
            </div>
            <div className="dashboard-hero__device">
              <div className="dashboard-hero__screen">
                <span className="dashboard-hero__screen-chip">CampusMate</span>
                <span className="dashboard-hero__screen-code">{"</>"}</span>
              </div>
              <div className="dashboard-hero__base" />
            </div>
          </div>
          <div className="dashboard-hero__panel dashboard-hero__panel--stack dashboard-hero__panel--books">
            <span className="dashboard-hero__book dashboard-hero__book--one" />
            <span className="dashboard-hero__book dashboard-hero__book--two" />
            <span className="dashboard-hero__book dashboard-hero__book--three" />
          </div>
          <div className="dashboard-hero__badge dashboard-hero__badge--quiz">✓</div>
          <div className="dashboard-hero__badge dashboard-hero__badge--spark">✦</div>
          <div className="dashboard-hero__badge dashboard-hero__badge--code">{"{"} {"}"}</div>
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
          <QuickActionCard
            label="History"
            description="Review your saved work."
            path="/history"
            icon="history"
            actionLabel="Open History"
          />
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
    </div>
  );
}

export function AskAiPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");
  const textareaRef = useRef(null);
  const threadEndRef = useRef(null);

  const suggestions = [
    { question: "What is the difference between TCP and UDP?", icon: "network", label: "Networking" },
    { question: "Explain object-oriented programming simply.", icon: "code", label: "Programming" },
    { question: "How does subnetting work?", icon: "network", label: "Computer networks" },
    { question: "Create a short Python practice task.", icon: "brain", label: "Practice task" },
  ];
  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  function resizeTextarea() {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  }

  function selectSuggestion(value) {
    setQuestion(value);
    setValidationError("");
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      resizeTextarea();
    });
  }

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
    const assistantMessageId = `${Date.now()}-assistant`;
    setMessages((current) => [
      ...current,
      { id: `${Date.now()}-user`, role: "user", content: trimmedQuestion },
      { id: assistantMessageId, role: "assistant", content: "" },
    ]);
    setQuestion("");
    requestAnimationFrame(resizeTextarea);

    try {
      await askQuestionStream(trimmedQuestion, {
        onChunk: (chunk, currentAnswer) => {
          setMessages((current) => current.map((message) => (
            message.id === assistantMessageId
              ? { ...message, content: currentAnswer || chunk }
              : message
          )));
        },
        onDone: (finalAnswer) => {
          setMessages((current) => current.map((message) => (
            message.id === assistantMessageId ? { ...message, content: finalAnswer } : message
          )));
        },
      });
    } catch (err) {
      setMessages((current) => current.filter((message) => message.id !== assistantMessageId));
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't complete this request. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="tool-page ask-chat">
      {messages.length === 0 ? (
        <div className="ask-chat__welcome">
          <div className="ask-chat__welcome-icon" aria-hidden="true">
            <Icon name="spark" />
          </div>
          <p className="eyebrow">Ask AI</p>
          <h2>Ask CampusMate a study question.</h2>
          <p className="ask-chat__description">Get clear explanations, solve difficult questions, and learn faster with your personal AI study assistant.</p>
          <div className="ask-chat__suggestions" aria-label="Suggested questions">
            {suggestions.map((suggestion) => (
              <button
                className="ask-suggestion"
                type="button"
                key={suggestion.question}
                onClick={() => selectSuggestion(suggestion.question)}
              >
                <span className="ask-suggestion__icon" aria-hidden="true"><Icon name={suggestion.icon} /></span>
                <span className="ask-suggestion__copy">
                  <span className="ask-suggestion__label">{suggestion.label}</span>
                  <span className="ask-suggestion__question">{suggestion.question}</span>
                </span>
                <Icon name="arrow" />
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="ask-chat__thread">
          {messages.map((message) => (
            <div className={`chat-message chat-message--${message.role}`} key={message.id}>
              {message.role === "assistant" ? (
                <div className="chat-message__avatar" aria-hidden="true"><Icon name="spark" /></div>
              ) : null}
              <div className="chat-message__content">
                {message.role === "assistant" ? <span className="chat-message__name">CampusMate</span> : null}
                {message.role === "assistant" ? (
                  message.content ? <MarkdownResponse className="chat-answer" content={message.content} /> : null
                ) : <div className="chat-bubble">{message.content}</div>}
                {message.role === "assistant" && message.content ? (
                  <button
                    className="copy-answer"
                    type="button"
                    onClick={() => navigator.clipboard?.writeText(message.content)}
                  >
                    <Icon name="copy" /> Copy answer
                  </button>
                ) : null}
              </div>
            </div>
          ))}
          {loading ? (
            <div className="chat-message chat-message--assistant chat-message--loading" role="status" aria-label="CampusMate is thinking">
              <div className="chat-message__avatar" aria-hidden="true"><Icon name="spark" /></div>
              <div className="typing-indicator"><span /><span /><span /></div>
            </div>
          ) : null}
          <div ref={threadEndRef} />
        </div>
      )}

      <form className="tool-form ask-chat__composer" onSubmit={handleSubmit}>
        <Field
          label="Message"
          htmlFor="ask-question"
          error={validationError}
          required
        >
          <TextAreaField
            id="ask-question"
            ref={textareaRef}
            rows={1}
            placeholder="Ask CampusMate anything…"
            value={question}
            onChange={(event) => {
              setQuestion(event.target.value);
              setValidationError("");
              resizeTextarea();
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
        </Field>

        <div className="form-actions">
          <button className="ask-chat__send" type="submit" disabled={loading || !question.trim()} aria-label="Send question">
            <Icon name="arrow-up" />
          </button>
        </div>
      </form>

      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}
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
    <section className="tool-page explain-page">
      <div className="tool-page__intro explain-page__intro">
        <div className="ask-chat__welcome-icon explain-page__icon" aria-hidden="true">
          <Icon name="lightbulb" />
        </div>
        <p className="eyebrow">EXPLAIN TOPIC</p>
        <h2>Understand any topic at your level</h2>
        <p>Choose a topic and difficulty, then get a clear explanation.</p>
      </div>

      <form className="tool-form explain-form" onSubmit={handleSubmit}>
        <Field label="Topic" htmlFor="explain-topic" error={validationError} required>
          <InputField
            id="explain-topic"
            type="text"
            placeholder="Enter a topic you want to understand..."
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />
        </Field>

        <div className="explain-difficulty">
          <span className="field__label">Difficulty</span>
          <div className="explain-difficulty__options" role="radiogroup" aria-label="Difficulty">
            {DIFFICULTY_OPTIONS.map((option) => (
              <button
                key={option.value}
                className={difficulty === option.value ? "is-selected" : ""}
                type="button"
                role="radio"
                aria-checked={difficulty === option.value}
                onClick={() => setDifficulty(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <ActionButton className="explain-submit" type="submit" disabled={loading}>
            <span>{loading ? "Creating explanation..." : "Generate Explanation"}</span>
          </ActionButton>
        </div>
      </form>

      {loading ? <LoadingNotice text="Creating explanation..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {explanation ? (
        <section className="result-panel explain-result">
          <div className="result-panel__header">
            <h3>Explanation</h3>
          </div>
          <MarkdownResponse className="result-panel__body" content={explanation} />
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
    <section className="tool-page summarize-page">
      <div className="tool-page__intro summarize-page__intro">
        <div className="ask-chat__welcome-icon summarize-page__icon" aria-hidden="true">
          <Icon name="summary" />
        </div>
        <p className="eyebrow">SUMMARIZE</p>
        <h2>Turn long material into useful study notes.</h2>
        <p>Paste your text, choose a style, then get a clear study summary.</p>
      </div>

      <form className="tool-form summarize-form" onSubmit={handleSubmit}>
        <Field
          label="Source text"
          htmlFor="summary-text"
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

        <div className="summarize-style">
          <span className="field__label">Summary style</span>
          <div className="summarize-style__options" role="radiogroup" aria-label="Summary style">
            {SUMMARY_STYLE_OPTIONS.map((option) => (
              <button
                key={option.value}
                className={style === option.value ? "is-selected" : ""}
                type="button"
                role="radio"
                aria-checked={style === option.value}
                onClick={() => setStyle(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <ActionButton className="summarize-submit" type="submit" disabled={loading}>
            {loading ? "Summarizing..." : "Summarize Text"}
          </ActionButton>
        </div>
      </form>

      {loading ? <LoadingNotice text="Summarizing..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {summary ? (
        <section className="result-panel summarize-result">
          <div className="result-panel__header">
            <h3>Summary</h3>
          </div>
          <MarkdownResponse className="result-panel__body result-panel__body--markdown" content={summary} />
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
    <section className="tool-page quiz-page">
      <div className="tool-page__intro quiz-page__intro">
        <div className="ask-chat__welcome-icon quiz-page__icon" aria-hidden="true">
          <Icon name="quiz" />
        </div>
        <p className="eyebrow">QUIZ</p>
        <h2>Generate a practice quiz and submit your answers.</h2>
        <p>Choose a topic, difficulty, and question count to create a focused practice quiz.</p>
      </div>

      <form className="tool-form quiz-form" onSubmit={handleGenerate}>
        <Field label="Topic" htmlFor="quiz-topic" error={validationError} required>
          <InputField
            id="quiz-topic"
            type="text"
            placeholder="Enter a topic you want to practice..."
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
          />
        </Field>

        <div className="quiz-difficulty">
          <span className="field__label">Difficulty</span>
          <div className="quiz-difficulty__options" role="radiogroup" aria-label="Difficulty">
            {DIFFICULTY_OPTIONS.map((option) => (
              <button
                key={option.value}
                className={difficulty === option.value ? "is-selected" : ""}
                type="button"
                role="radio"
                aria-checked={difficulty === option.value}
                onClick={() => setDifficulty(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-count">
          <span className="field__label">Number of questions</span>
          <div className="quiz-count__options" role="radiogroup" aria-label="Number of questions">
            {QUIZ_COUNT_OPTIONS.map((option) => (
              <button
                key={option}
                className={questionCount === String(option) ? "is-selected" : ""}
                type="button"
                role="radio"
                aria-checked={questionCount === String(option)}
                onClick={() => setQuestionCount(String(option))}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <ActionButton className="quiz-submit" type="submit" disabled={loadingGenerate}>
            {loadingGenerate ? "Generating quiz..." : "Generate Quiz"}
          </ActionButton>
        </div>
      </form>

      {loadingGenerate ? <LoadingNotice text="Generating quiz..." /> : null}
      {error ? <StatusBanner tone="error" icon="alert" title="Request failed" message={error} /> : null}

      {scoreResult ? (
        <section
          className={`quiz-score-banner ${Number(scoreResult.score_percentage) >= 50 ? "is-passed" : "needs-practice"}`}
          role="status"
          aria-label={`Quiz score ${scoreResult.score_percentage}%`}
        >
          <div className="quiz-score-banner__main">
            <span className="quiz-score-banner__eyebrow">Quiz completed</span>
            <strong>{scoreResult.score_percentage}%</strong>
            <span className="quiz-score-banner__status">
              {Number(scoreResult.score_percentage) >= 50 ? "Passed" : "Keep practicing"}
            </span>
          </div>
          <div className="quiz-score-banner__details">
            <span>{scoreResult.correct_answers} of {scoreResult.total_questions} answers correct</span>
            <div className="quiz-score-banner__track" aria-hidden="true">
              <div
                className="quiz-score-banner__fill"
                style={{ width: `${Math.max(0, Math.min(100, Number(scoreResult.score_percentage) || 0))}%` }}
              />
            </div>
          </div>
        </section>
      ) : null}

      {quiz ? (
        <section className="result-panel">
          <div className="result-panel__header result-panel__header--stack">
            <div>
              <h3>{quiz.topic} Quiz</h3>
              <p>{quiz.difficulty} level, {quiz.questions.length} questions</p>
            </div>
            <ActionButton type="button" variant="secondary" onClick={handleSubmitQuiz} disabled={loadingSubmit}>
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
  const [reloadToken, setReloadToken] = useState(0);
  const [openHistoryItem, setOpenHistoryItem] = useState("");
  const [deletingHistoryItem, setDeletingHistoryItem] = useState("");

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
  }, [reloadToken]);

  const questions = Array.isArray(history?.questions) ? history.questions : [];
  const quizzes = Array.isArray(history?.quizzes) ? history.quizzes : [];
  const interactions = Array.isArray(history?.interactions) ? history.interactions : [];
  const hasInteractionHistory = interactions.length > 0;
  const hasActivity = hasInteractionHistory || questions.length > 0 || quizzes.length > 0;

  async function handleDeleteHistoryItem(section, index, key) {
    setDeletingHistoryItem(key);
    setError("");

    try {
      await deleteHistoryItem(section, index);
      setOpenHistoryItem("");
      setReloadToken((value) => value + 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "CampusMate couldn't delete this history item. Please try again.");
    } finally {
      setDeletingHistoryItem("");
    }
  }

  return (
    <section className="tool-page history-page">
      <div className="tool-page__intro history-page__intro">
        <div className="ask-chat__welcome-icon history-page__icon" aria-hidden="true">
          <Icon name="history" />
        </div>
        <p className="eyebrow">HISTORY</p>
        <h2>Review your stored questions and quizzes.</h2>
        <p>See your recent AI activity, saved explanations, summaries, and completed quizzes.</p>
      </div>

      {loading ? <LoadingNotice text="Loading history..." /> : null}
      {error ? (
        <div className="history-error">
          <StatusBanner tone="error" icon="alert" title="History unavailable" message={error} />
          <div className="form-actions">
            <ActionButton type="button" variant="secondary" onClick={() => setReloadToken((value) => value + 1)}>
              Retry loading history
            </ActionButton>
          </div>
        </div>
      ) : null}

      {!loading && !error && !hasActivity ? (
        <EmptyState
          title="No study history yet."
          description="Ask a question or complete a quiz and your activity will appear here."
        />
      ) : null}

      {!loading && !error && hasActivity ? (
        <div className="history-overview">
          <div className="history-overview__item">
            <strong>{hasInteractionHistory ? interactions.length : questions.length + quizzes.length}</strong>
            <span>AI interactions</span>
          </div>
          <div className="history-overview__item">
            <strong>{quizzes.length}</strong>
            <span>Quizzes completed</span>
          </div>
        </div>
      ) : null}

      {hasInteractionHistory ? (
        <section className="section-block history-activity">
          <div className="section-block__header">
            <h3>AI Activity</h3>
            <p>Every question, explanation, summary and quiz is saved with its date and time.</p>
          </div>
          <div className="history-list">
            {[...interactions]
              .map((item, index) => ({ item, index }))
              .sort((left, right) => new Date(right.item.created_at) - new Date(left.item.created_at))
              .map(({ item, index }) => {
                let quizDetails = null;
                if (item.type === "quiz") {
                  try {
                    quizDetails = JSON.parse(item.output);
                  } catch {
                    quizDetails = null;
                  }
                }
                const itemKey = `interactions-${index}`;
                const isOpen = openHistoryItem === itemKey;
                const preview = quizDetails
                  ? `Quiz generated with ${quizDetails.questions?.length ?? 0} questions at ${quizDetails.difficulty} level.`
                  : previewText(item.output);

                return (
                  <article className={`history-entry history-entry--interaction ${isOpen ? "is-open" : ""}`} key={itemKey}>
                    <div className="history-entry__row">
                      <button
                        className="history-entry__summary"
                        type="button"
                        aria-expanded={isOpen}
                        onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}
                      >
                        <span className="history-entry__folder" aria-hidden="true"><Icon name="history" /></span>
                        <span className="history-entry__summary-text">
                          <span className="history-entry__topline">
                            <span className="history-entry__type">{item.title || "AI Activity"}</span>
                            <time dateTime={item.created_at}>{formatInteractionDate(item.created_at)}</time>
                          </span>
                          <strong>{item.input}</strong>
                          <span className="history-entry__preview">{preview}</span>
                        </span>
                      </button>
                      <button
                        className="history-entry__more"
                        type="button"
                        aria-expanded={isOpen}
                        onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}
                      >
                        {isOpen ? "Less" : "More"}
                      </button>
                      <button
                        className="history-entry__delete"
                        type="button"
                        disabled={deletingHistoryItem === itemKey}
                        onClick={() => handleDeleteHistoryItem("interactions", index, itemKey)}
                      >
                        {deletingHistoryItem === itemKey ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                    {isOpen ? (
                      <div className="history-entry__details">
                        {quizDetails ? (
                          <p>Quiz generated with {quizDetails.questions?.length ?? 0} questions at {quizDetails.difficulty} level.</p>
                        ) : (
                          <MarkdownResponse className="history-entry__response" content={item.output} />
                        )}
                      </div>
                    ) : null}
                  </article>
                );
              })}
          </div>
        </section>
      ) : null}

      {!hasInteractionHistory && questions.length > 0 ? (
        <section className="section-block">
          <div className="section-block__header">
            <h3>Questions</h3>
            <p>Original question and answer saved by the backend.</p>
          </div>
          <div className="history-list">
            {questions.map((item, index) => (
              (() => {
                const itemKey = `questions-${index}`;
                const isOpen = openHistoryItem === itemKey;
                const preview = previewText(item.answer);

                return (
                  <article className={`history-entry ${isOpen ? "is-open" : ""}`} key={itemKey}>
                    <div className="history-entry__row">
                      <button className="history-entry__summary" type="button" aria-expanded={isOpen} onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}>
                        <span className="history-entry__folder" aria-hidden="true"><Icon name="history" /></span>
                        <span className="history-entry__summary-text">
                          <span className="history-entry__type">Question</span>
                          <strong>{item.question}</strong>
                          <span className="history-entry__preview">{preview}</span>
                        </span>
                      </button>
                      <button className="history-entry__more" type="button" aria-expanded={isOpen} onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}>
                        {isOpen ? "Less" : "More"}
                      </button>
                      <button className="history-entry__delete" type="button" disabled={deletingHistoryItem === itemKey} onClick={() => handleDeleteHistoryItem("questions", index, itemKey)}>
                        {deletingHistoryItem === itemKey ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                    {isOpen ? (
                      <div className="history-entry__details">
                        <MarkdownResponse className="history-entry__response" content={item.answer} />
                      </div>
                    ) : null}
                  </article>
                );
              })()
            ))}
          </div>
        </section>
      ) : null}

      {!hasInteractionHistory && quizzes.length > 0 ? (
        <section className="section-block">
          <div className="section-block__header">
            <h3>Completed Quizzes</h3>
            <p>Persisted quiz results from the backend storage.</p>
          </div>
          <div className="history-list">
            {quizzes.map((item, index) => (
              (() => {
                const itemKey = `quizzes-${index}`;
                const isOpen = openHistoryItem === itemKey;
                const preview = `Difficulty: ${item.difficulty} | Score: ${item.score_percentage}% | Correct: ${item.correct_answers}/${item.total_questions}`;

                return (
                  <article className={`history-entry ${isOpen ? "is-open" : ""}`} key={itemKey}>
                    <div className="history-entry__row">
                      <button className="history-entry__summary" type="button" aria-expanded={isOpen} onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}>
                        <span className="history-entry__folder" aria-hidden="true"><Icon name="history" /></span>
                        <span className="history-entry__summary-text">
                          <span className="history-entry__type">Quiz</span>
                          <strong>{item.topic}</strong>
                          <span className="history-entry__preview">{preview}</span>
                        </span>
                      </button>
                      <button className="history-entry__more" type="button" aria-expanded={isOpen} onClick={() => setOpenHistoryItem(isOpen ? "" : itemKey)}>
                        {isOpen ? "Less" : "More"}
                      </button>
                      <button className="history-entry__delete" type="button" disabled={deletingHistoryItem === itemKey} onClick={() => handleDeleteHistoryItem("quizzes", index, itemKey)}>
                        {deletingHistoryItem === itemKey ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                    {isOpen ? (
                      <div className="history-entry__details">
                        <p>
                          Difficulty: {item.difficulty} | Score: {item.score_percentage}% | Correct: {item.correct_answers}/
                          {item.total_questions}
                        </p>
                      </div>
                    ) : null}
                  </article>
                );
              })()
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
  const [reloadToken, setReloadToken] = useState(0);

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
  }, [reloadToken]);

  const averageScore = Number(stats?.average_quiz_score) || 0;
  const answeredTotal = (Number(stats?.correct_answers) || 0) + (Number(stats?.incorrect_answers) || 0);

  return (
    <section className="tool-page statistics-page">
      <div className="tool-page__intro statistics-page__intro">
        <div className="ask-chat__welcome-icon statistics-page__icon" aria-hidden="true">
          <Icon name="statistics" />
        </div>
        <p className="eyebrow">STATISTICS</p>
        <h2>Track your real study activity.</h2>
        <p>See your questions, quizzes, answers, and progress from the backend statistics store.</p>
        <button className="statistics-refresh" type="button" disabled={loading} onClick={() => setReloadToken((value) => value + 1)}>
          {loading ? "Refreshing..." : "Refresh stats"}
        </button>
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

          <section className="result-panel statistics-score">
            <div className="result-panel__header">
              <h3>Average Quiz Score</h3>
              <p>{answeredTotal} total answers checked</p>
            </div>
            <div className="score-meter" aria-label={`Average quiz score ${formatAverageScore(stats.average_quiz_score)}`}>
              <div className="score-meter__value">{formatAverageScore(stats.average_quiz_score)}</div>
              <div className="score-meter__track">
                <div className="score-meter__fill" style={{ width: `${Math.max(0, Math.min(100, averageScore))}%` }} />
              </div>
              <p className="score-meter__caption">Updated from your saved CampusMate activity.</p>
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
