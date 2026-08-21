import { Link, NavLink, useLocation } from "react-router-dom";
import { NAV_ITEMS, PAGE_META } from "./appData";

function Icon({ name }) {
  const commonProps = {
    "aria-hidden": true,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };

  switch (name) {
    case "dashboard":
      return (
        <svg {...commonProps}>
          <path d="M4 11.5h7V4H4z" />
          <path d="M13 20h7v-7h-7z" />
          <path d="M13 4h7v4h-7z" />
          <path d="M4 15h7v5H4z" />
        </svg>
      );
    case "ask":
      return (
        <svg {...commonProps}>
          <path d="M12 3a8 8 0 0 0-6.9 12.1L4 21l5.9-1.2A8 8 0 1 0 12 3Z" />
          <path d="M9.5 11.5h.01" />
          <path d="M12 11.5h.01" />
          <path d="M14.5 11.5h.01" />
        </svg>
      );
    case "lightbulb":
      return (
        <svg {...commonProps}>
          <path d="M9 18h6" />
          <path d="M10 22h4" />
          <path d="M8 15a6 6 0 1 1 8 0c-.8.8-1 1.4-1 3H9c0-1.6-.2-2.2-1-3Z" />
        </svg>
      );
    case "summary":
      return (
        <svg {...commonProps}>
          <path d="M7 6h10" />
          <path d="M7 10h10" />
          <path d="M7 14h6" />
          <path d="M7 18h8" />
        </svg>
      );
    case "quiz":
      return (
        <svg {...commonProps}>
          <path d="M8 7h8" />
          <path d="M8 11h8" />
          <path d="M8 15h4" />
          <rect x="4" y="4" width="16" height="16" rx="3" />
        </svg>
      );
    case "history":
      return (
        <svg {...commonProps}>
          <path d="M4 12a8 8 0 1 0 2.3-5.7" />
          <path d="M4 4v4h4" />
          <path d="M12 8v4l3 2" />
        </svg>
      );
    case "statistics":
    case "chart":
      return (
        <svg {...commonProps}>
          <path d="M5 19V5" />
          <path d="M5 19h14" />
          <path d="M8 16v-4" />
          <path d="M12 16V8" />
          <path d="M16 16v-6" />
        </svg>
      );
    case "menu":
      return (
        <svg {...commonProps}>
          <path d="M4 7h16" />
          <path d="M4 12h16" />
          <path d="M4 17h16" />
        </svg>
      );
    case "close":
      return (
        <svg {...commonProps}>
          <path d="M6 6l12 12" />
          <path d="M18 6 6 18" />
        </svg>
      );
    case "arrow":
      return (
        <svg {...commonProps}>
          <path d="M5 12h12" />
          <path d="m13 6 6 6-6 6" />
        </svg>
      );
    case "check":
      return (
        <svg {...commonProps}>
          <path d="M20 6 9 17l-5-5" />
        </svg>
      );
    case "alert":
      return (
        <svg {...commonProps}>
          <path d="M12 9v4" />
          <path d="M12 17h.01" />
          <path d="M10.3 4.5h3.4l7 12.1a2 2 0 0 1-1.7 3H4.9a2 2 0 0 1-1.7-3z" />
        </svg>
      );
    case "spark":
      return (
        <svg {...commonProps}>
          <path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z" />
        </svg>
      );
    case "user":
      return (
        <svg {...commonProps}>
          <path d="M20 21a8 8 0 1 0-16 0" />
          <circle cx="12" cy="8" r="4" />
        </svg>
      );
    default:
      return null;
  }
}

export function Sidebar({ mobileOpen, onClose }) {
  return (
    <aside className={`sidebar ${mobileOpen ? "is-open" : ""}`} aria-label="Primary navigation">
      <div className="sidebar__brand">
        <div className="brand-mark" aria-hidden="true">
          CM
        </div>
        <div>
          <div className="brand-title">CampusMate AI</div>
          <div className="brand-subtitle">Study assistant</div>
        </div>
        <button className="icon-button sidebar__close" type="button" onClick={onClose} aria-label="Close navigation">
          <Icon name="close" />
        </button>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) => `nav-link ${isActive ? "is-active" : ""}`}
            onClick={onClose}
          >
            <span className="nav-link__icon">
              <Icon name={item.icon} />
            </span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        <p>Organize questions, explanations, summaries, and quizzes in one place.</p>
      </div>
    </aside>
  );
}

export function Header({ onMenuClick }) {
  const location = useLocation();
  const meta = PAGE_META[location.pathname] ?? PAGE_META["/"];

  return (
    <header className="topbar">
      <div className="topbar__left">
        <button className="icon-button topbar__menu" type="button" onClick={onMenuClick} aria-label="Open navigation">
          <Icon name="menu" />
        </button>
        <div>
          <h1 className="page-title">{meta.title}</h1>
          <p className="page-subtitle">{meta.subtitle}</p>
        </div>
      </div>

      <div className="profile-chip" aria-label="Student profile">
        <span className="profile-chip__avatar" aria-hidden="true">
          <Icon name="user" />
        </span>
        <span className="profile-chip__text">
          <span className="profile-chip__name">Student</span>
          <span className="profile-chip__role">Learner</span>
        </span>
      </div>
    </header>
  );
}

export function AppLayout({ children, mobileNavOpen, onMenuClick, onCloseMobileNav }) {
  return (
    <div className="app-layout">
      <div
        className={`app-overlay ${mobileNavOpen ? "is-visible" : ""}`}
        onClick={onCloseMobileNav}
        aria-hidden="true"
      />
      <Sidebar mobileOpen={mobileNavOpen} onClose={onCloseMobileNav} />
      <div className="app-layout__content">
        <Header onMenuClick={onMenuClick} />
        <main className="main-content">
          <div className="main-content__inner">{children}</div>
        </main>
      </div>
    </div>
  );
}

export function StatCard({ label, value, hint, icon }) {
  return (
    <article className="stat-card">
      <div className="stat-card__icon" aria-hidden="true">
        <Icon name={icon} />
      </div>
      <div className="stat-card__body">
        <div className="stat-card__value">{value}</div>
        <div className="stat-card__label">{label}</div>
        <div className="stat-card__hint">{hint}</div>
      </div>
    </article>
  );
}

export function QuickActionCard({ label, description, path, icon, actionLabel }) {
  return (
    <Link className="quick-card" to={path}>
      <div className="quick-card__icon" aria-hidden="true">
        <Icon name={icon} />
      </div>
      <div className="quick-card__content">
        <h3>{label}</h3>
        <p>{description}</p>
      </div>
      <span className="quick-card__action">
        {actionLabel}
        <Icon name="arrow" />
      </span>
    </Link>
  );
}

export function EmptyState({ title, description }) {
  return (
    <section className="empty-state">
      <div className="empty-state__icon" aria-hidden="true">
        <Icon name="history" />
      </div>
      <div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </section>
  );
}

export function Field({ label, hint, error, children, required = false, htmlFor }) {
  const errorId = htmlFor ? `${htmlFor}-error` : undefined;

  return (
    <div className={`field ${error ? "has-error" : ""}`}>
      <div className="field__label-row">
        <label className="field__label" htmlFor={htmlFor}>
          {label}
          {required ? <span aria-hidden="true"> *</span> : null}
        </label>
        {hint ? <span className="field__hint">{hint}</span> : null}
      </div>
      {children}
      {error ? (
        <p id={errorId} className="field__error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function TextAreaField(props) {
  return <textarea className="form-control form-control--textarea" {...props} />;
}

export function InputField(props) {
  return <input className="form-control" {...props} />;
}

export function SelectField(props) {
  return <select className="form-control" {...props} />;
}

export function ActionButton({ children, variant = "primary", ...props }) {
  return (
    <button className={`action-button action-button--${variant}`} {...props}>
      {children}
    </button>
  );
}

export function StatusBanner({ tone = "info", title, message, icon = "spark" }) {
  if (!title && !message) {
    return null;
  }

  return (
    <div className={`status-banner status-banner--${tone}`} role={tone === "error" ? "alert" : "status"}>
      <div className="status-banner__icon" aria-hidden="true">
        <Icon name={icon} />
      </div>
      <div className="status-banner__body">
        {title ? <strong>{title}</strong> : null}
        {message ? <p>{message}</p> : null}
      </div>
    </div>
  );
}

export function MetricCard({ label, value, hint, icon }) {
  return <StatCard label={label} value={value} hint={hint} icon={icon} />;
}

export function QuizQuestionCard({ index, question, selectedAnswer, onChange, disabled = false }) {
  return (
    <fieldset className="quiz-card" disabled={disabled}>
      <legend className="quiz-card__legend">
        Question {index}
      </legend>
      <p className="quiz-card__question">{question.question}</p>
      <div className="quiz-options" role="radiogroup" aria-label={`Question ${index}`}>
        {["A", "B", "C", "D"].map((option) => {
          const optionId = `question-${index}-option-${option}`;
          const isChecked = selectedAnswer === option;

          return (
            <label key={option} className={`quiz-option ${isChecked ? "is-selected" : ""}`} htmlFor={optionId}>
              <input
                id={optionId}
                type="radio"
                name={`question-${index}`}
                value={option}
                checked={isChecked}
                onChange={() => onChange(option)}
              />
              <span className="quiz-option__key">{option}</span>
              <span className="quiz-option__text">{question.options[option]}</span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
