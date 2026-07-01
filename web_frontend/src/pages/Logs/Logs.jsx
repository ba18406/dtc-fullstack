import { useEffect, useState } from "react";
import * as XLSX from "xlsx";
import { getActivityLogs } from "../../services/logService";
import "../../styles/dashboard.css";
import "../../styles/users.css";

function Logs() {
  const [logs, setLogs] = useState([]);
  const [searchText, setSearchText] = useState("");

  async function loadLogs() {
    try {
      const data = await getActivityLogs();

      if (data.success) {
        setLogs(data.logs || []);
      } else {
        alert(data.error || "Unable to load logs.");
      }
    } catch (err) {
      console.error(err);
      alert("API error while loading logs.");
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((item) => {
    const text = `${item.id} ${item.username} ${item.action_type} ${item.target_file} ${item.log_time}`.toLowerCase();
    return text.includes(searchText.toLowerCase());
  });

  function exportLogsToExcel() {
    const exportData = filteredLogs.map((item) => ({
      ID: item.id,
      Username: item.username,
      Action: item.action_type,
      "Target File": item.target_file || "",
      "Log Time": item.log_time,
    }));

    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();

    XLSX.utils.book_append_sheet(workbook, worksheet, "Activity Logs");
    XLSX.writeFile(workbook, "activity_logs.xlsx");
  }

  return (
    <div className="dashboard-page">
      <div className="page-title">
        <h1>Activity Logs</h1>
        <p>Monitor system actions and export logs</p>
      </div>

      <div className="users-toolbar">
        <input
          type="text"
          placeholder="Search logs..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />

        <div>
          <button className="secondary-btn" onClick={loadLogs}>
            Refresh
          </button>

          <button className="primary-btn" onClick={exportLogsToExcel}>
            Export Excel
          </button>
        </div>
      </div>

      <div className="panel">
        <h3>Activity Logs</h3>

        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Action</th>
              <th>Target File</th>
              <th>Log Time</th>
            </tr>
          </thead>

          <tbody>
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan="5">No logs found.</td>
              </tr>
            ) : (
              filteredLogs.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.username}</td>
                  <td>
                    <span className={`action-badge ${String(item.action_type).toLowerCase()}`}>
                      {item.action_type}
                    </span>
                  </td>
                  <td>{item.target_file || "-"}</td>
                  <td>{item.log_time}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Logs;