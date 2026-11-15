
import { useState } from "react";
import api from "../api";

function Feedback() {
  const [formData, setFormData] = useState({
    agent_id: "",
    post_id: "",
    notification_id: "",
    feedback: "relevant",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await api.post("/feedback", formData);

      alert("Feedback submitted successfully!");

      setFormData({
        agent_id: "",
        post_id: "",
        notification_id: "",
        feedback: "relevant",
      });
    } catch (error) {
      alert(
        JSON.stringify(
          error.response?.data?.detail || error.message,
          null,
          2
        )
      );
    }
  };

  
return (
  <div className="page-container">
    <h1>Submit Agent Feedback</h1>

    <form
  onSubmit={handleSubmit}
  style={{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "15px"
  }}
>
      <input
        placeholder="Agent ID"
        value={formData.agent_id}
        onChange={(e) =>
          setFormData({ ...formData, agent_id: e.target.value })
        }
        required
      />

      <input
        placeholder="Post ID"
        value={formData.post_id}
        onChange={(e) =>
          setFormData({ ...formData, post_id: e.target.value })
        }
        required
      />

      <input
        placeholder="Notification ID"
        value={formData.notification_id}
        onChange={(e) =>
          setFormData({ ...formData, notification_id: e.target.value })
        }
        required
      />

      <select
        value={formData.feedback}
        onChange={(e) =>
          setFormData({ ...formData, feedback: e.target.value })
        }
      >
        <option value="relevant">Relevant</option>
        <option value="not_relevant">Not Relevant</option>
      </select>

      <button type="submit">Submit Feedback</button>
    </form>
  </div>
);

}

export default Feedback;
