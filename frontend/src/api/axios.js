import axios from "axios";
import { getToken } from "../utils/storage";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "https://ai-workspace-eqfg.onrender.com",
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