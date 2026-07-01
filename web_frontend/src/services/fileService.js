import { API_URL } from "../config/apiConfig";

export async function getVisibleFiles(userId, role, username) {
  const response = await fetch(
    `${API_URL}/files/visible/${userId}/${role}/${username}`
  );

  if (!response.ok) {
    throw new Error("Unable to load files.");
  }

  return await response.json();
}

export async function uploadFile(file, uploadedBy) {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("uploaded_by", uploadedBy);

  const response = await fetch(`${API_URL}/files/upload`, {
    method: "POST",
    body: formData,
  });

  return await response.json();
}

export function getDownloadUrl(fileId) {
  return `${API_URL}/files/download/${fileId}`;
}

export async function deleteFile(fileId, userId, role, username) {
  const response = await fetch(
    `${API_URL}/files/delete/${fileId}/${userId}/${role}/${username}`,
    {
      method: "DELETE",
    }
  );

  return await response.json();
}