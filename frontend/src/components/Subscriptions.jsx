import { useState } from "react";
import api from "../api";

function Subscriptions() {
  const [agentId, setAgentId] = useState("");
  const [targetAgentId, setTargetAgentId] = useState("");
  const [subscriptions, setSubscriptions] = useState([]);

  const fetchSubscriptions = async () => {
    try {
      const response = await api.get(`/subscriptions/${agentId}`);
      const data = response.data;
      setSubscriptions(data.subscriptions || data);
    } catch (error) {
      alert("Unable to load subscriptions");
    }
  };

  const createSubscription = async (e) => {
    e.preventDefault();

    try {
      await api.post("/subscriptions", {
        agent_id: agentId,
        target_agent_id: targetAgentId,
      });

      alert("Subscription created successfully!");
      setTargetAgentId("");
      fetchSubscriptions();
    } catch (error) {
      alert(error.response?.data?.detail || "Subscription failed");
    }
  };

  
return (
  <div className="page-container">
    <h1>Agent Subscriptions</h1>

    <form
  onSubmit={createSubscription}
  style={{
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "15px"
  }}
>
      <input
        placeholder="Your Agent ID"
        value={agentId}
        onChange={(e) => setAgentId(e.target.value)}
        required
      />

      <input
        placeholder="Target Agent ID"
        value={targetAgentId}
        onChange={(e) => setTargetAgentId(e.target.value)}
        required
      />

      <button type="submit">Subscribe</button>

      <button type="button" onClick={fetchSubscriptions}>
        Load Subscriptions
      </button>
    </form>

    <div className="card-grid">
      {subscriptions.map((item) => (
        <div className="item-card" key={item.subscription_id || item._id}>
          <h3>{item.agent_name}</h3>
          <p>Company: {item.company_name}</p>
          <p>Agent ID: {item.target_agent_id}</p>
        </div>
      ))}
    </div>
  </div>
);

}

export default Subscriptions;
