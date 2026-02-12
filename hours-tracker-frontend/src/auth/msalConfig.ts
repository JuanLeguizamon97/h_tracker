import { type Configuration, LogLevel } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_AZURE_CLIENT_ID ?? "";
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID ?? "";
const redirectUri = import.meta.env.VITE_AZURE_REDIRECT_URI ?? "http://localhost:5173";

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri,
    postLogoutRedirectUri: redirectUri,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
      loggerCallback: (_level, message) => {
        console.debug("[MSAL]", message);
      },
    },
  },
};

const apiScope = import.meta.env.VITE_AZURE_API_SCOPE ?? "";

export const loginRequest = {
  scopes: apiScope ? [apiScope] : ["openid", "profile", "email"],
};

export const apiTokenRequest = {
  scopes: apiScope ? [apiScope] : [],
};
