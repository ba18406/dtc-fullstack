import { API_URL } from "../config/apiConfig";

export async function getVisibleUsers(userId, role) {
  const response = await fetch(`${API_URL}/users/visible/${userId}/${role}`);

  if (!response.ok) {
    throw new Error("Unable to load users.");
  }

  return await response.json();
}

export async function addUser(userData) {
  const response = await fetch(`${API_URL}/users/add`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });

  return await response.json();
}

export async function updateUser(userData) {
  const response = await fetch(`${API_URL}/users/update`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });

  return await response.json();
}

export async function deleteUser(userId) {
  const response = await fetch(`${API_URL}/users/delete/${userId}`, {
    method: "DELETE",
  });

  return await response.json();
}