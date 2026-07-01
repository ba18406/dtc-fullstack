import { API_URL } from "../config/apiConfig";

export async function getRecentUploads() {
  const response = await fetch(`${API_URL}/uploads/recent`);

  if (!response.ok) {
    throw new Error("Unable to load recent uploads.");
  }

  return await response.json();
}