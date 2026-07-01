function DashboardCard({ title, value, description, icon }) {
  return (
    <div className="dashboard-card">
      <div className="dashboard-card-icon">{icon}</div>
      <div>
        <span>{title}</span>
        <h2>{value}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default DashboardCard;