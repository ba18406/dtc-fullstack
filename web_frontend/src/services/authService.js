import API_CONFIG from "../config/apiConfig";
import { addActivityLog } from "./logService";

const API_URL = API_CONFIG.BASE_URL;

export async function loginUser(username, password) {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Login failed.");
  }

  if (!data.success) {
    throw new Error(data.message || "Login failed.");
  }

localStorage.setItem("dtc_user", JSON.stringify(data));

try {
  await addActivityLog(
    data.user.id,
    "LOGIN",
    data.user.username
  );
} catch (err) {
  console.error("Unable to write login log:", err);
}

return data;
}

export function logoutUser() {
  localStorage.removeItem("dtc_user");
}

export function getCurrentUser() {
  const user = localStorage.getItem("dtc_user");
  return user ? JSON.parse(user) : null;
}