import { type ReactNode } from "react";
import {
  useIsAuthenticated,
  useMsal,
  MsalAuthenticationTemplate,
} from "@azure/msal-react";
import { InteractionType } from "@azure/msal-browser";
import { loginRequest } from "./msalConfig.ts";

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="text-gray-600">Authenticating...</p>
      </div>
    </div>
  );
}

function ErrorFallback({ error }: { error: unknown }) {
  const { instance } = useMsal();
  const message =
    error instanceof Error ? error.message : "Authentication failed";

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="max-w-md rounded-lg bg-white p-8 text-center shadow-lg">
        <h2 className="mb-2 text-xl font-semibold text-red-600">
          Sign-in Error
        </h2>
        <p className="mb-6 text-gray-600">{message}</p>
        <button
          onClick={() => instance.loginRedirect(loginRequest)}
          className="rounded-md bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

export default function ProtectedRoute({
  children,
}: {
  children: ReactNode;
}) {
  const isAuthenticated = useIsAuthenticated();

  if (!isAuthenticated) {
    return (
      <MsalAuthenticationTemplate
        interactionType={InteractionType.Redirect}
        authenticationRequest={loginRequest}
        loadingComponent={LoadingFallback}
        errorComponent={({ error }) => <ErrorFallback error={error} />}
      >
        {children}
      </MsalAuthenticationTemplate>
    );
  }

  return <>{children}</>;
}
