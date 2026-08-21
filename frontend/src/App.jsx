import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AppLayout } from "./components";
import { DashboardPage, PlaceholderPage } from "./pages";

const PLACEHOLDERS = [
  {
    path: "/ask-ai",
    title: "Ask AI",
    description: "Ask CampusMate questions about the topics you're studying.",
  },
  {
    path: "/explain-topic",
    title: "Explain Topic",
    description: "Explore a topic at the level that feels right for you.",
  },
  {
    path: "/summarize",
    title: "Summarize",
    description: "Turn long material into shorter study notes.",
  },
  {
    path: "/quiz",
    title: "Quiz",
    description: "Generate practice questions for the topic you want to review.",
  },
  {
    path: "/history",
    title: "History",
    description: "Review your earlier questions and completed quizzes.",
  },
  {
    path: "/statistics",
    title: "Statistics",
    description: "Track your study activity and progress over time.",
  },
];

function Shell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    document.body.style.overflow = mobileNavOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileNavOpen]);

  useEffect(() => {
    setMobileNavOpen(false);
  }, [location.pathname]);

  return (
    <AppLayout
      mobileNavOpen={mobileNavOpen}
      onMenuClick={() => setMobileNavOpen(true)}
      onCloseMobileNav={() => setMobileNavOpen(false)}
    >
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        {PLACEHOLDERS.map((page) => (
          <Route
            key={page.path}
            path={page.path}
            element={<PlaceholderPage title={page.title} description={page.description} />}
          />
        ))}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Shell />
    </BrowserRouter>
  );
}
