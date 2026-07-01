import { getCurrentUser } from "../../services/authService";
import { API_URL } from "../../config/apiConfig";
import "../../styles/dashboard.css";
import "../../styles/users.css";

function Settings() {
  const currentUser = getCurrentUser();
  const user = currentUser?.user || currentUser;

  return (
    <div className="dashboard-page">
      <div className="page-title">
        <h1>Settings</h1>
        <p>Manage profile, system information and application preferences</p>
      </div>

      <div className="settings-grid">
        <div className="panel">
          <h3>Profile Information</h3>

          <div className="settings-row">
            <span>Username</span>
            <strong>{user?.username || "-"}</strong>
          </div>

          <div className="settings-row">
            <span>Full Name</span>
            <strong>{user?.full_name || "-"}</strong>
          </div>

          <div className="settings-row">
            <span>Role</span>
            <strong>{user?.role || "-"}</strong>
          </div>

          <div className="settings-row">
            <span>User ID</span>
            <strong>{user?.id || "-"}</strong>
          </div>
        </div>

        <div className="panel">
          <h3>System Information</h3>

          <div className="settings-row">
            <span>API Server</span>
            <strong>{API_URL}</strong>
          </div>

          <div className="settings-row">
            <span>Backend</span>
            <strong>FastAPI</strong>
          </div>

          <div className="settings-row">
            <span>Database</span>
            <strong>Supabase PostgreSQL</strong>
          </div>

          <div className="settings-row">
            <span>Storage</span>
            <strong>Supabase Storage</strong>
          </div>
        </div>

        <div className="panel">
          <h3>Theme</h3>

          <div className="settings-row">
            <span>Current Theme</span>
            <strong>Light Mode</strong>
          </div>

          <div className="settings-row">
            <span>Dark Mode</span>
            <strong>Coming Soon</strong>
          </div>
        </div>

        <div className="panel">
          <h3>About</h3>

          <div className="settings-row">
            <span>Application</span>
            <strong>DTC Enterprise</strong>
          </div>

          <div className="settings-row">
            <span>Version</span>
            <strong>1.0</strong>
          </div>

          <div className="settings-row">
            <span>Built With</span>
            <strong>React + FastAPI + Supabase</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;