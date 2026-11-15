
import { useEffect, useState } from "react";
import api from "../api";

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/agents")
      .then((response) => {
        const data = response.data;
        setAgents(data.agents || data);
      })
      .catch((error) => {
        console.error("Agents error:", error);
        setError(error.message || "Unable to load agents");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="page-container">
      <h1>AI Agents</h1>

      {loading && <p>Loading agents...</p>}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {!loading && !error && agents.length === 0 && (
        <p>No agents found.</p>
      )}

      <div className="card-grid">
        {agents.map((agent) => (
          <div className="item-card" key={agent._id}>
            <h3>{agent.agent_name}</h3>
            <p><strong>Company:</strong> {agent.company_name}</p>
            <p><strong>Industry:</strong> {agent.industry}</p>
            <p><strong>Description:</strong> {agent.description}</p>
            <p>
              <strong>Interests:</strong>{" "}
              {agent.interests.join(", ")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Agents;
