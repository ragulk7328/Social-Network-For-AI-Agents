import { useEffect, useState } from "react";
import api from "../api";

function Analytics() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    api.get("/analytics/relevance")
      .then((response) => {
        setAnalytics(response.data);
      })
      .catch((error) => {
        console.error("Analytics error:", error);
      });
  }, []);

  
return (
  <div className="page-container">
    <h1>Relevance Analytics</h1>

    {analytics ? (
      <div className="card-grid">
        <div className="item-card">
          <h3>Total Feedback</h3>
          <h2>{analytics.total_feedback}</h2>
        </div>

        <div className="item-card">
          <h3>Relevant Feedback</h3>
          <h2>{analytics.relevant_count}</h2>
        </div>

        <div className="item-card">
          <h3>Not Relevant</h3>
          <h2>{analytics.not_relevant_count}</h2>
        </div>

        <div className="item-card">
          <h3>Total Notifications</h3>
          <h2>{analytics.total_notifications}</h2>
        </div>

        <div className="item-card">
          <h3>Relevance Percentage</h3>
          <h2>{analytics.relevance_percentage}%</h2>
        </div>
      </div>
    ) : (
      <p>Loading analytics...</p>
    )}
  </div>
);

}

export default Analytics;