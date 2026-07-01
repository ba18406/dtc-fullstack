import { useEffect, useState } from "react";
import { getCurrentUser } from "../../services/authService";
import { getDashboardStats } from "../../services/dashboardService";
import { getRecentUploads } from "../../services/uploadService";
import { getActivityLogs } from "../../services/logService";
import DashboardCard from "../../components/DashboardCard";
import DashboardChart from "../../components/DashboardChart";
import RecentUploads from "../../components/RecentUploads";
import ActivityPanel from "../../components/ActivityPanel";
import QuickActions from "../../components/QuickActions";
import "../../styles/dashboard.css";

function Dashboard() {
  const currentUser = getCurrentUser();
  const user = currentUser?.user || currentUser;

  const [stats, setStats] = useState({
    total_users: 0,
    total_files: 0,
    my_files: 0,
  });

  const [uploads, setUploads] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getDashboardStats(user.id);

        if (data.success) {
          setStats(data.stats);
        }

        const uploadsData = await getRecentUploads();

        if (uploadsData.success) {
          setUploads(uploadsData.uploads);
        }

        const logsData = await getActivityLogs();

        if (logsData.success) {
          setLogs(logsData.logs.slice(0, 5));
        }
      } catch (err) {
        console.error(err);
      }
    }

    if (user?.id) {
      loadDashboard();
    }
  }, []);

  return (
    <div className="dashboard-page">
      <div className="page-title">
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.full_name || user?.username || "User"}</p>
      </div>

      <div className="stats-grid">
        <DashboardCard
          title="Total Users"
          value={stats.total_users}
          description="Registered users"
          icon="👥"
        />

        <DashboardCard
          title="Total Files"
          value={stats.total_files}
          description="Uploaded documents"
          icon="📁"
        />

        <DashboardCard
          title="My Files"
          value={stats.my_files}
          description="Your uploaded files"
          icon="📤"
        />

        <DashboardCard
          title="Role"
          value={user?.role || "User"}
          description="Current permission level"
          icon="🛡️"
        />
      </div>

      <DashboardChart />

      <div className="dashboard-grid">
        <RecentUploads uploads={uploads} />
        <ActivityPanel logs={logs} />
      </div>

      <QuickActions />
    </div>
  );
}

export default Dashboard;