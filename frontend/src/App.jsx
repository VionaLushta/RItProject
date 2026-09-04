import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AppLayout } from "./components";
import {
  AskAiPage,
  DashboardPage,
  ExplainTopicPage,
  HistoryPage,
  QuizPage,
  StatisticsPage,
  SummarizePage,
} from "./pages";

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
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [location.pathname]);

  return (
    <AppLayout
      mobileNavOpen={mobileNavOpen}
      onMenuClick={() => setMobileNavOpen(true)}
      onCloseMobileNav={() => setMobileNavOpen(false)}
    >
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/ask-ai" element={<AskAiPage />} />
        <Route path="/explain-topic" element={<ExplainTopicPage />} />
        <Route path="/summarize" element={<SummarizePage />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/statistics" element={<StatisticsPage />} />
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
