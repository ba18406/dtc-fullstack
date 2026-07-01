import { API_URL } from "../config/apiConfig";

export async function getDashboardStats(userId) {
    const response = await fetch(`${API_URL}/dashboard/stats/${userId}`);

    if (!response.ok) {
        throw new Error("Unable to load dashboard statistics.");
    }

    return await response.json();
}