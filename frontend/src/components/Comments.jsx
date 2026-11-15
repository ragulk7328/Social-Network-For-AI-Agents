
import { useState } from "react";
import api from "../api";

function Comments() {
  const [postId, setPostId] = useState("");
  const [comments, setComments] = useState([]);
  const [totalComments, setTotalComments] = useState(0);

  const fetchComments = async () => {
    if (!postId.trim()) {
      alert("Please enter Post ID");
      return;
    }

    try {
      const response = await api.get(`/comments/${postId}`);

      setComments(response.data.comments || []);
      setTotalComments(response.data.total_comments || 0);
    } catch (error) {
      console.error(error);
      alert("Unable to load comments");
    }
  };

  return (
    <div className="page-container">
      <h1>AI Agent Comments</h1>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "15px",
          marginBottom: "30px"
        }}
      >
        <input
          placeholder="Enter Post ID"
          value={postId}
          onChange={(e) => setPostId(e.target.value)}
        />

        <button onClick={fetchComments}>
          Load Comments
        </button>
      </div>

      <h3 style={{ textAlign: "center", marginBottom: "20px" }}>
        Total Comments: {totalComments}
      </h3>

      <div className="card-grid">
        {comments.map((comment) => (
          <div className="item-card" key={comment._id}>
            <h3>{comment.agent_name || comment.agent_id || "AI Agent"}</h3>

            <p>{comment.content}</p>

            <p>
              <strong>AI Generated:</strong>{" "}
              {comment.is_autonomous ? "Yes" : "No"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Comments;
