import apiClient from "./client.ts";

export interface AppUser {
  id: string;
  azure_oid: string;
  email: string | null;
  display_name: string | null;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

export async function fetchCurrentUser(): Promise<AppUser> {
  const { data } = await apiClient.get<AppUser>("/auth/me");
  return data;
}
