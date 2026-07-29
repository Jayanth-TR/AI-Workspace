import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

// Interceptor to handle Content-Type dynamically for FormData vs JSON
api.interceptors.request.use((config) => {
    if (config.data instanceof FormData) {
        delete config.headers["Content-Type"];
    } else if (!config.headers["Content-Type"]) {
        config.headers["Content-Type"] = "application/json";
    }
    return config;
});

export default api;