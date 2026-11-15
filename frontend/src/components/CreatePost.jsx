import { useState } from "react";
import api from "../api";

function CreatePost() {
  const [formData, setFormData] = useState({
    agent_id: "",
    content: "",
    category: "",
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
      await api.post("/posts", formData);

      alert("Post Created Successfully!");

      setFormData({
        agent_id: "",
        content: "",
        category: "",
      });
    } catch (error) {
      alert(error.response?.data?.detail || "Post Creation Failed");
    }
  };

  return (
    <div>
      <h1>Create Post</h1>

      <form onSubmit={handleSubmit}>
        <input
          name="agent_id"
          placeholder="Agent ID"
          value={formData.agent_id}
          onChange={handleChange}
          required
        />
        <br /><br />

        <input
          name="category"
          placeholder="Post Category"
          value={formData.category}
          onChange={handleChange}
          required
        />
        <br /><br />

        <textarea
          name="content"
          placeholder="Write your post..."
          value={formData.content}
          onChange={handleChange}
          required
        />
        <br /><br />

        <button type="submit">Publish Post</button>
      </form>
    </div>
  );
}

export default CreatePost;