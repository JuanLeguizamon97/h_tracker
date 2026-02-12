import { useMsal } from "@azure/msal-react";
import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "../api/auth.ts";

export default function DashboardPage() {
  const { instance } = useMsal();
  const account = instance.getActiveAccount();

  const { data: user, isLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: fetchCurrentUser,
    retry: 1,
  });

  const handleLogout = () => {
    instance.logoutRedirect({ postLogoutRedirectUri: "/" });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-bold text-gray-900">
            Impact Point Hours Tracker
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {account?.name ?? user?.display_name ?? "User"}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-md border border-gray-300 px-4 py-1.5 text-sm text-gray-700 hover:bg-gray-100"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          </div>
        ) : (
          <>
            <div className="mb-8 rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-800">
                Welcome, {user?.display_name ?? account?.name ?? "User"}
              </h2>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <dt className="text-sm text-gray-500">Email</dt>
                  <dd className="font-medium text-gray-900">
                    {user?.email ?? account?.username ?? "-"}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Last login</dt>
                  <dd className="font-medium text-gray-900">
                    {user?.last_login_at
                      ? new Date(user.last_login_at).toLocaleString()
                      : "-"}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Status</dt>
                  <dd className="font-medium text-gray-900">
                    {user?.is_active ? "Active" : "Inactive"}
                  </dd>
                </div>
              </dl>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Employees", href: "/employees" },
                { label: "Clients", href: "/clients" },
                { label: "Projects", href: "/projects" },
                { label: "Time Entries", href: "/time-entries" },
              ].map((card) => (
                <a
                  key={card.href}
                  href={card.href}
                  className="rounded-lg border bg-white p-6 shadow-sm transition hover:shadow-md"
                >
                  <h3 className="text-lg font-semibold text-gray-800">
                    {card.label}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Manage {card.label.toLowerCase()}
                  </p>
                </a>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
