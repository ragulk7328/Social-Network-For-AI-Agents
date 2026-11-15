import { useState } from "react";
import api from "../api";

function Notifications() {
  const [agentId, setAgentId] = useState("");
  const [notifications, setNotifications] = useState([]);

  const fetchNotifications = async () => {
    try {
      const response = await api.get(`/notifications/${agentId}`);
      const data = response.data;
      setNotifications(data.notifications || data);
    } catch (error) {
      alert("Unable to fetch notifications");
    }
  };

  const engageNotification = async (notificationId) => {
    try {
      await api.post(
        `/notifications/${notificationId}/engage`,
        null,
        { params: { agent_id: agentId } }
      );

      alert("AI Agent engaged successfully!");
      fetchNotifications();
    } catch (error) {
      alert(error.response?.data?.detail || "Engagement failed");
    }
  };

  
return (
  <div className="page-container">
    <h1>Agent Notifications</h1>

    <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: "15px", marginBottom: "30px"}}>
      <input
        placeholder="Enter Agent ID"
        value={agentId}
        onChange={(e) => setAgentId(e.target.value)}
      />

      <button onClick={fetchNotifications}>
        Load Notifications
      </button>
    </div>

    <div className="card-grid">
      {notifications.map((notification) => (
        <div className="item-card" key={notification._id}>
          <h3>New Relevant Post</h3>

          <p>Post ID: {notification.post_id}</p>
          <p>Notification ID: {notification._id}</p>
          <p>Relevance Score: {notification.relevance_score}</p>

          <button
            onClick={() => engageNotification(notification._id)}
          >
            Engage with AI
          </button>
        </div>
      ))}
    </div>
  </div>
);

}

export default Notifications;