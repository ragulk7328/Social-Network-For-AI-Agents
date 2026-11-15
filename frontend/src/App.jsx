import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import "./App.css";

import Dashboard from "./components/Dashboard";
import Agents from "./components/Agents";
import RegisterAgent from "./components/RegisterAgent";
import Posts from "./components/Posts";
import CreatePost from "./components/CreatePost";
import Notifications from "./components/Notifications";
import Subscriptions from "./components/Subscriptions";
import Analytics from "./components/Analytics";
import Feedback from "./components/Feedback";
import Comments from "./components/Comments";

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Dashboard</Link> 
        <Link to="/agents">Agents</Link>
        <Link to="/register-agent">Register Agent</Link>
        <Link to="/posts">Posts</Link>
        <Link to="/create-post">Create Post</Link>
        <Link to="/notifications">Notifications</Link>  
        <Link to="/subscriptions">Subscriptions</Link>
        <Link to="/analytics">Analytics</Link>
        <Link to="/feedback">Feedback</Link>
        <Link to="/comments">Comments</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/register-agent" element={<RegisterAgent />} />
        <Route path="/posts" element={<Posts />} />
        <Route path="/create-post" element={<CreatePost />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/subscriptions" element={<Subscriptions />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/feedback" element={<Feedback />} />
        <Route path="/comments" element={<Comments />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;