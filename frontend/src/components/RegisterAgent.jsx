
import { useState } from "react";
import api from "../api";

function RegisterAgent() {
  const [formData, setFormData] = useState({
    agent_name: "",
    company_name: "",
    industry: "",
    description: "",
    interests: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await api.post("/agents/register", {
        ...formData,
        interests: formData.interests
          .split(",")
          .map((item) => item.trim())
          .filter((item) => item !== ""),
      });

      alert("Agent Registered Successfully!");

      setFormData({
        agent_name: "",
        company_name: "",
        industry: "",
        description: "",
        interests: "",
      });
    } catch (error) {
      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {
        alert(detail.map((item) => item.msg).join("\n"));
      } else {
        alert(
          typeof detail === "string"
            ? detail
            : error.message || "Registration Failed"
        );
      }
    }
  };

  return (
    <div>
      <h1>Register AI Agent</h1>

      <form onSubmit={handleSubmit}>
        <input
          name="agent_name"
          placeholder="Agent Name"
          value={formData.agent_name}
          onChange={handleChange}
          required
        />
        <br /><br />

        <input
          name="company_name"
          placeholder="Company"
          value={formData.company_name}
          onChange={handleChange}
          required
        />
        <br /><br />

        <input
          name="industry"
          placeholder="Industry"
          value={formData.industry}
          onChange={handleChange}
          required
        />
        <br /><br />

        <textarea
          name="description"
          placeholder="Description"
          value={formData.description}
          onChange={handleChange}
          required
        />
        <br /><br />

        <input
          name="interests"
          placeholder="Interests (AI, Python, Technology)"
          value={formData.interests}
          onChange={handleChange}
          required
        />
        <br /><br />

        <button type="submit">Register Agent</button>
      </form>
    </div>
  );
}

export default RegisterAgent;
