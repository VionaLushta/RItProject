export const NAV_ITEMS = [
  { label: "Dashboard", path: "/", icon: "dashboard" },
  { label: "Ask AI", path: "/ask-ai", icon: "ask" },
  { label: "Explain Topic", path: "/explain-topic", icon: "lightbulb" },
  { label: "Summarize", path: "/summarize", icon: "summary" },
  { label: "Quiz", path: "/quiz", icon: "quiz" },
  { label: "History", path: "/history", icon: "history" },
  { label: "Statistics", path: "/statistics", icon: "statistics" },
];

export const QUICK_ACTIONS = [
  {
    label: "Ask AI",
    description: "Get help with a study question.",
    path: "/ask-ai",
    icon: "ask",
    actionLabel: "Open Ask AI",
  },
  {
    label: "Explain a Topic",
    description: "Understand a topic at your level.",
    path: "/explain-topic",
    icon: "lightbulb",
    actionLabel: "Open Explain Topic",
  },
  {
    label: "Summarize Text",
    description: "Turn long material into clear notes.",
    path: "/summarize",
    icon: "summary",
    actionLabel: "Open Summarize",
  },
  {
    label: "Generate Quiz",
    description: "Test yourself on any topic.",
    path: "/quiz",
    icon: "quiz",
    actionLabel: "Open Quiz",
  },
];

export const PAGE_META = {
  "/": {
    title: "Dashboard",
    subtitle: "Your study tools, organized in one place.",
  },
  "/ask-ai": {
    title: "Ask AI",
    subtitle: "Ask a study question and get a clear answer.",
  },
  "/explain-topic": {
    title: "Explain Topic",
    subtitle: "Explore a topic at the level you need.",
  },
  "/summarize": {
    title: "Summarize",
    subtitle: "Turn long text into a cleaner study version.",
  },
  "/quiz": {
    title: "Quiz",
    subtitle: "Generate a multiple-choice quiz for practice.",
  },
  "/history": {
    title: "History",
    subtitle: "Review your past questions and quiz attempts.",
  },
  "/statistics": {
    title: "Statistics",
    subtitle: "Track your study activity and progress.",
  },
};

export const DASHBOARD_STATS = [
  { label: "Questions Asked", value: "0", hint: "Awaiting backend data", icon: "ask" },
  { label: "Quizzes Completed", value: "0", hint: "Awaiting backend data", icon: "quiz" },
  { label: "Correct Answers", value: "0", hint: "Awaiting backend data", icon: "statistics" },
  { label: "Average Score", value: "0.0%", hint: "Awaiting backend data", icon: "chart" },
];
