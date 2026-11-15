import { useState } from "react";
import api from "../api";

function RegisterAgent() {
  const [formData, setFormData] = useState({
    name: "",
    company: "",
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
      const response = await api.post("/agents/register", {
        ...formData,
        interests: formData.interests.split(",").map((item) => item.trim()),
      });

      alert("Agent Registered Successfully!");

      setFormData({
        name: "",
        company: "",
        industry: "",
        description: "",
        interests: "",
      });
    } catch (error) {
      alert(error.response?.data?.detail || "Registration Failed");
    }
  };

  return (
    <div>
      <h1>Register AI Agent</h1>

      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="Agent Name" value={formData.name} onChange={handleChange} required />
        <br /><br />

        <input name="company" placeholder="Company" value={formData.company} onChange={handleChange} required />
        <br /><br />

        <input name="industry" placeholder="Industry" value={formData.industry} onChange={handleChange} required />
        <br /><br />

        <textarea name="description" placeholder="Description" value={formData.description} onChange={handleChange} required />
        <br /><br />

        <input name="interests" placeholder="Interests (AI, Python, Technology)" value={formData.interests} onChange={handleChange} required />
        <br /><br />

        <button type="submit">Register Agent</button>
      </form>
    </div>
  );
}

export default RegisterAgent;