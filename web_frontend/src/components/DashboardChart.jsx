import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const uploadData = [
  { day: "Mon", uploads: 2 },
  { day: "Tue", uploads: 4 },
  { day: "Wed", uploads: 3 },
  { day: "Thu", uploads: 6 },
  { day: "Fri", uploads: 5 },
];

const roleData = [
  { name: "Admin", value: 1 },
  { name: "Supervisor", value: 2 },
  { name: "User", value: 8 },
];

function DashboardChart() {
  return (
    <div className="dashboard-grid">
      <div className="panel chart-panel">
        <h3>Upload Trend</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={uploadData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="uploads" stroke="#1e3a8a" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="panel chart-panel">
        <h3>Users by Role</h3>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie data={roleData} dataKey="value" nameKey="name" outerRadius={80} label>
              {roleData.map((entry, index) => (
                <Cell key={index} fill={["#1e3a8a", "#2563eb", "#60a5fa"][index]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default DashboardChart;