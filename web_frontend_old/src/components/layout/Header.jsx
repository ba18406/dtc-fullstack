import { useNavigate } from "react-router-dom";
import { getCurrentUser, logoutUser } from "../../services/authService";
import "../../styles/header.css";

function Header() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  function handleLogout() {
    logoutUser();
    navigate("/login");
  }

  return (
    <header className="header">
      <div>
        <h2>Data Tracking Center</h2>
        <p>Enterprise Web Dashboard</p>
      </div>

      <div className="header-user">
        <span>{user?.username || "User"}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
}

export default Header;