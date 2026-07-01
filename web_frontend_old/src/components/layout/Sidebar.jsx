import { NavLink } from "react-router-dom";
import "../../styles/sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">DTC</div>

      <nav>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/users">Users</NavLink>
        <NavLink to="/files">Files</NavLink>
        <NavLink to="/logs">Logs</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;