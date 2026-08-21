import { DASHBOARD_STATS, QUICK_ACTIONS } from "./appData";
import { EmptyState, QuickActionCard, StatCard } from "./components";

export function DashboardPage() {
  return (
    <div className="dashboard">
      <section className="dashboard-hero">
        <div className="dashboard-hero__copy">
          <p className="eyebrow">CampusMate AI</p>
          <h2>Welcome to CampusMate AI</h2>
          <p>Your study tools, organized in one place.</p>
        </div>
      </section>

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
          <p>Backend data will appear here after integration.</p>
        </div>
        <div className="stats-grid">
          {DASHBOARD_STATS.map((item) => (
            <StatCard key={item.label} {...item} />
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-block__header">
          <h3>Recent Activity</h3>
          <p>Your latest study activity will show up here.</p>
        </div>
        <EmptyState
          title="No study activity yet."
          description="Your recent questions and quizzes will appear here."
        />
      </section>
    </div>
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
