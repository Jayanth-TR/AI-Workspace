/* eslint-disable react-refresh/only-export-components */
import { createContext, useEffect, useState } from "react";

import authService from "../services/authService";

import {
    saveToken,
    getToken,
    removeToken,
    saveUser,
    removeUser,
} from "../utils/storage";

import api from "../api/axios";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Login
    const login = async (loginData) => {
        try {
            const response = await authService.login(loginData);
            const token = response?.access_token;

            if (!token) {
                return {
                    success: false,
                    message: response?.message || "Invalid email address or password.",
                };
            }

            saveToken(token);
            api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

            const currentUser = await authService.getCurrentUser();
            saveUser(currentUser);
            setUser(currentUser);
            setIsAuthenticated(true);

            return {
                success: true,
            };
        } catch (error) {
            return {
                success: false,
                message:
                    error.response?.data?.detail ||
                    "Invalid email address or password.",
            };
        }
    };

    // Register
    const register = async (registerData) => {
        try {
            await authService.register(registerData);
            return {
                success: true,
            };
        } catch (error) {
            return {
                success: false,
                message:
                    error.response?.data?.detail ||
                    "Registration failed",
            };
        }
    };

    // Logout
    const logout = () => {
        removeToken();
        removeUser();
        delete api.defaults.headers.common["Authorization"];
        setUser(null);
        setIsAuthenticated(false);
    };

    // Auto Login
    useEffect(() => {
        const initializeAuth = async () => {
            const token = getToken();

            if (!token) {
                setLoading(false);
                return;
            }

            try {
                api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
                const currentUser = await authService.getCurrentUser();
                saveUser(currentUser);
                setUser(currentUser);
                setIsAuthenticated(true);
            } catch {
                removeToken();
                removeUser();
                delete api.defaults.headers.common["Authorization"];
                setUser(null);
                setIsAuthenticated(false);
            }

            setLoading(false);
        };

        initializeAuth();
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                isAuthenticated,
                login,
                register,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
