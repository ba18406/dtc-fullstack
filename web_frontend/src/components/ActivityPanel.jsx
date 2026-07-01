function ActivityPanel({ logs }) {
  return (
    <div className="panel">
      <h3>Recent Activity</h3>

      <ul className="activity-list">
        {logs.length === 0 ? (
          <li>No activity logs found.</li>
        ) : (
          logs.map((log) => (
            <li key={log.id}>
              <div>
                <strong>{log.username}</strong>
                <span>{log.action_type}</span>
              </div>
              <small>{log.log_time}</small>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default ActivityPanel;