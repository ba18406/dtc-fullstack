import { useEffect, useState } from "react";
import { getCurrentUser } from "../../services/authService";
import {
  getVisibleUsers,
  addUser,
  updateUser,
  deleteUser,
} from "../../services/userService";
import "../../styles/dashboard.css";
import "../../styles/users.css";
import { addActivityLog } from "../../services/logService";

function Users() {
  const currentUser = getCurrentUser();
  const user = currentUser?.user || currentUser;

  const [users, setUsers] = useState([]);
  const [searchText, setSearchText] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState("add");
  const [selectedUser, setSelectedUser] = useState(null);

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    full_name: "",
    role: "user",
    supervisor_id: "",
  });

  async function loadUsers() {
    try {
      const data = await getVisibleUsers(user.id, user.role);

      if (data.success) {
        setUsers(data.users);
      }
    } catch (err) {
      console.error(err);
      alert("Unable to load users.");
    }
  }

  useEffect(() => {
    if (user?.id && user?.role) {
      loadUsers();
    }
  }, []);

  function openAddModal() {
    setModalMode("add");
    setSelectedUser(null);
    setFormData({
      username: "",
      password: "",
      full_name: "",
      role: "user",
      supervisor_id: "",
    });
    setShowModal(true);
  }

  function openViewModal(item) {
    setModalMode("view");
    setSelectedUser(item);
    setFormData({
      username: item.username,
      password: "",
      full_name: item.full_name,
      role: item.role,
      supervisor_id: item.supervisor_id || "",
    });
    setShowModal(true);
  }

  function openEditModal(item) {
    setModalMode("edit");
    setSelectedUser(item);
    setFormData({
      username: item.username,
      password: "",
      full_name: item.full_name,
      role: item.role,
      supervisor_id: item.supervisor_id || "",
    });
    setShowModal(true);
  }

  async function handleSave() {
    try {
      if (!formData.username || !formData.full_name) {
        alert("Username and full name are required.");
        return;
      }

      if (modalMode === "add" && !formData.password) {
        alert("Password is required for new users.");
        return;
      }

      let result;

      if (modalMode === "add") {
        result = await addUser({
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
          role: formData.role,
          supervisor_id: formData.supervisor_id || null,
        });
        await addActivityLog(
            user.id,
            "ADD USER",
            formData.username
        );
      }

      if (modalMode === "edit") {
        result = await updateUser({
          user_id: selectedUser.id,
          username: formData.username,
          password: formData.password || null,
          full_name: formData.full_name,
          role: formData.role,
          supervisor_id: formData.supervisor_id || null,
        });
        await addActivityLog(
            user.id,
            "EDIT USER",
            formData.username
        );
      }

      if (result.success) {
        alert("User saved successfully.");
        setShowModal(false);
        loadUsers();
      } else {
        alert(result.error || "Operation failed.");
      }
    } catch (err) {
      console.error(err);
      alert("API error.");
    }
  }

  async function handleDelete(item) {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete user: ${item.username}?`
    );

    if (!confirmDelete) return;

    try {
      const result = await deleteUser(item.id);

      if (result.success) {
        alert("User deleted successfully.");
        await addActivityLog(
            user.id,
            "DELETE USER",
            item.username
        );
        loadUsers();
      } else {
        alert(result.error || "Delete failed.");
      }
    } catch (err) {
      console.error(err);
      alert("API error.");
    }
  }

  const filteredUsers = users.filter((item) => {
    const text = `${item.username} ${item.full_name} ${item.role}`.toLowerCase();
    return text.includes(searchText.toLowerCase());
  });

  return (
    <div className="dashboard-page">
      <div className="page-title">
        <h1>Users Management</h1>
        <p>Manage system users and permissions</p>
      </div>

      <div className="users-toolbar">
        <input
          type="text"
          placeholder="Search users..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />

        <div>
          <button className="primary-btn" onClick={openAddModal}>
            + Add User
          </button>

          <button className="secondary-btn" onClick={loadUsers}>
            Refresh
          </button>
        </div>
      </div>

      <div className="panel">
        <h3>Visible Users</h3>

        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Full Name</th>
              <th>Role</th>
              <th>Supervisor ID</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredUsers.length === 0 ? (
              <tr>
                <td colSpan="6">No users found.</td>
              </tr>
            ) : (
              filteredUsers.map((item) => (
                <tr key={item.id} onDoubleClick={() => handlePreview(item)}>                  <td>{item.id}</td>
                  <td>{item.username}</td>
                  <td>{item.full_name}</td>
                  <td>
                    <span className={`role-badge ${item.role}`}>
                      {item.role}
                    </span>
                  </td>
                  <td>{item.supervisor_id || "-"}</td>
                  <td>
                    <button className="table-btn" onClick={() => openViewModal(item)}>
                      View
                    </button>

                    <button className="table-btn" onClick={() => openEditModal(item)}>
                      Edit
                    </button>

                    <button
                      className="table-btn danger"
                      onClick={() => handleDelete(item)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="user-modal">
            <h2>
              {modalMode === "add" && "Add User"}
              {modalMode === "view" && "View User"}
              {modalMode === "edit" && "Edit User"}
            </h2>

            <label>Username</label>
            <input
              type="text"
              value={formData.username}
              disabled={modalMode === "view"}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
            />

            <label>Password</label>
            <input
              type="password"
              placeholder={modalMode === "edit" ? "Leave blank to keep old password" : ""}
              value={formData.password}
              disabled={modalMode === "view"}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
            />

            <label>Full Name</label>
            <input
              type="text"
              value={formData.full_name}
              disabled={modalMode === "view"}
              onChange={(e) =>
                setFormData({ ...formData, full_name: e.target.value })
              }
            />

            <label>Role</label>
            <select
              value={formData.role}
              disabled={modalMode === "view"}
              onChange={(e) =>
                setFormData({ ...formData, role: e.target.value })
              }
            >
              <option value="admin">Admin</option>
              <option value="supervisor">Supervisor</option>
              <option value="user">User</option>
            </select>

            <label>Supervisor ID</label>
            <input
              type="number"
              value={formData.supervisor_id}
              disabled={modalMode === "view"}
              onChange={(e) =>
                setFormData({ ...formData, supervisor_id: e.target.value })
              }
            />

            <div className="modal-actions">
              <button className="secondary-btn" onClick={() => setShowModal(false)}>
                Close
              </button>

              {modalMode !== "view" && (
                <button className="primary-btn" onClick={handleSave}>
                  Save
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Users;