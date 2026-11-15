import type {
  AccessToken,
  AssistantAnswer,
  AssistantConversationTurn,
  CurrentAccount,
  ForecastItem,
  OperationalSummary,
  Order,
} from "./types";

const accessTokenStorageKey = "ifood-ai-copilot-access-token";
const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  const accessToken = sessionStorage.getItem(accessTokenStorageKey);
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${apiBaseUrl}${path}`, { ...init, headers });
  if (response.status === 401 && path !== "/auth/login") {
    sessionStorage.removeItem(accessTokenStorageKey);
    window.dispatchEvent(new Event("auth-expired"));
  }

  if (!response.ok) {
    const body = await response.text();
    let message = body || `A API respondeu com status ${response.status}.`;

    if (body) {
      try {
        const payload: { detail?: unknown } = JSON.parse(body);
        if (typeof payload.detail === "string") {
          message = payload.detail;
        }
      } catch {
        message = body;
      }
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function hasAccessToken(): boolean {
  return sessionStorage.getItem(accessTokenStorageKey) !== null;
}

export function storeAccessToken(accessToken: string): void {
  sessionStorage.setItem(accessTokenStorageKey, accessToken);
}

export function clearAccessToken(): void {
  sessionStorage.removeItem(accessTokenStorageKey);
}

export function login(username: string, password: string): Promise<AccessToken> {
  return request<AccessToken>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function getCurrentAccount(): Promise<CurrentAccount> {
  return request<CurrentAccount>("/auth/me");
}

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getDateRange(days: number): { startDate: string; endDate: string } {
  const end = new Date();
  const start = new Date(end);
  start.setDate(start.getDate() - days + 1);
  return { startDate: formatDate(start), endDate: formatDate(end) };
}

export function getSummary(
  restaurantId: string,
  days: number,
): Promise<OperationalSummary> {
  const { startDate, endDate } = getDateRange(days);
  const params = new URLSearchParams({
    restaurant_id: restaurantId,
    start_date: startDate,
    end_date: endDate,
  });
  return request<OperationalSummary>(`/analytics/summary?${params}`);
}

export function getOrders(restaurantId: string): Promise<Order[]> {
  const params = new URLSearchParams({
    restaurant_id: restaurantId,
    limit: "8",
    offset: "0",
  });
  return request<Order[]>(`/orders?${params}`);
}

export function getForecast(restaurantId: string): Promise<ForecastItem[]> {
  const params = new URLSearchParams({
    restaurant_id: restaurantId,
    days: "7",
    history_days: "90",
  });
  return request<{ forecast: ForecastItem[] }>(`/analytics/forecast?${params}`).then(
    (result) => result.forecast,
  );
}

export function askAssistant(
  restaurantId: string,
  question: string,
  history: AssistantConversationTurn[],
): Promise<AssistantAnswer> {
  return request<AssistantAnswer>("/assistant/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ restaurant_id: restaurantId, question, history }),
  });
}
