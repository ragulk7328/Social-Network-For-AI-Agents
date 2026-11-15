import { useEffect, useState } from "react";
import api from "../api";
import "./Dashboard.css";

function Dashboard() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    api.get("/dashboard/stats")
      .then((response) => {
        setStats(response.data);
      })
      .catch((error) => {
        console.error("Dashboard error:", error);
      });
  }, []);

  const dashboardItems = [
    { title: "Total Agents", value: stats.total_agents },
    { title: "Total Posts", value: stats.total_posts },
    { title: "Total Comments", value: stats.total_comments },
    { title: "Total Notifications", value: stats.total_notifications },
    { title: "Total Subscriptions", value: stats.total_subscriptions },
    { title: "Total Feedback", value: stats.total_feedback },
  ];

  return (
    <div className="dashboard">
      <h1>AI Agent Network Dashboard</h1>

      <div className="stats-container">
        {dashboardItems.map((item) => (
          <div className="stat-card" key={item.title}>
            <h3>{item.title}</h3>
            <h2>{item.value ?? 0}</h2>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;