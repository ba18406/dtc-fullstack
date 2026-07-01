import { NavLink } from "react-router-dom";
import "../../styles/sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">DTC</div>
        <div>
          <h2>DTC</h2>
          <p>Enterprise</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/">📊 Dashboard</NavLink>
        <NavLink to="/users">👥 Users</NavLink>
        <NavLink to="/files">📁 Files</NavLink>
        <NavLink to="/logs">📝 Logs</NavLink>
        <NavLink to="/settings">⚙️ Settings</NavLink>
      </nav>

      <div className="sidebar-footer">
        <p>FastAPI + Supabase</p>
      </div>
    </aside>
  );
}

export default Sidebar;