import axios from "axios";
import { getToken } from "../utils/storage";

const apiBaseURL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: apiBaseURL,
});

// Interceptor to handle Authorization header & Content-Type dynamically
api.interceptors.request.use((config) => {
    const token = getToken();
    if (token && token !== "undefined" && token !== "null") {
        config.headers["Authorization"] = `Bearer ${token}`;
    }

    if (config.data instanceof FormData) {
        delete config.headers["Content-Type"];
    } else if (!config.headers["Content-Type"]) {
        config.headers["Content-Type"] = "application/json";
    }
    return config;
});

export default api;