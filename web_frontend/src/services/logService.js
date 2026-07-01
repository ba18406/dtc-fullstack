import { API_URL } from "../config/apiConfig";

export async function getActivityLogs() {
  const response = await fetch(`${API_URL}/logs`);

  if (!response.ok) {
    throw new Error("Unable to load logs.");
  }

  return await response.json();
}

export async function addActivityLog(userId, actionType, targetFile = "") {
  const response = await fetch(`${API_URL}/logs/add`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      action_type: actionType,
      target_file: targetFile,
    }),
  });

  return await response.json();
}