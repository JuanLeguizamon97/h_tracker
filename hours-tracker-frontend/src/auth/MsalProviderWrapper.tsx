import { type ReactNode } from "react";
import {
  PublicClientApplication,
  EventType,
  type AuthenticationResult,
} from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "./msalConfig.ts";

const msalInstance = new PublicClientApplication(msalConfig);

// Set the first account as active if available after redirect
const accounts = msalInstance.getAllAccounts();
if (accounts.length > 0) {
  msalInstance.setActiveAccount(accounts[0]);
}

msalInstance.addEventCallback((event) => {
  if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
    const result = event.payload as AuthenticationResult;
    msalInstance.setActiveAccount(result.account);
  }
});

export { msalInstance };

export default function MsalProviderWrapper({
  children,
}: {
  children: ReactNode;
}) {
  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
}
