import axios from "axios";
import { msalInstance } from "../auth/MsalProviderWrapper.tsx";
import { apiTokenRequest } from "../auth/msalConfig.ts";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use(async (config) => {
  const account = msalInstance.getActiveAccount();
  if (!account) return config;

  try {
    const response = await msalInstance.acquireTokenSilent({
      ...apiTokenRequest,
      account,
    });
    config.headers.Authorization = `Bearer ${response.accessToken}`;
  } catch {
    // Silent token acquisition failed — trigger interactive login
    await msalInstance.acquireTokenRedirect(apiTokenRequest);
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired / invalid — re-authenticate
      await msalInstance.acquireTokenRedirect(apiTokenRequest);
    }
    return Promise.reject(error);
  },
);

export default apiClient;
