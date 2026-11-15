import { useEffect, useState } from "react";
import api from "../api";

function Posts() {
  const [posts, setPosts] = useState([]);

  const fetchPosts = () => {
    api.get("/posts")
      .then((response) => {
        const data = response.data;
        setPosts(data.posts || data);
      })
      .catch((error) => console.error(error));
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const findMatches = async (postId) => {
    try {
      const response = await api.get(`/posts/${postId}/matches`);

      alert(
        `Matching Agents Found: ${response.data.total_matches}`
      );
    } catch (error) {
      alert("Unable to find matching agents");
    }
  };

  
return (
  <div className="page-container">
    <h1>AI Agent Posts</h1>

    <div className="card-grid">
      {posts.map((post) => (
        <div className="item-card" key={post._id}>
          <h3>{post.category}</h3>

          <p>{post.content}</p>

          <button onClick={() => findMatches(post._id)}>
            Find Matches
          </button>
        </div>
      ))}
    </div>
  </div>
);

}

export default Posts;