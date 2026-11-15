export type OrderStatus = "pending" | "preparing" | "delivered" | "cancelled";

export interface Order {
  id: string;
  restaurant_id: string;
  amount: string;
  items_count: number;
  status: OrderStatus;
  created_at: string;
}

export interface HourMetric {
  hour: number;
  orders: number;
}

export interface OperationalSummary {
  restaurant_id: string;
  total_orders: number;
  completed_orders: number;
  cancelled_orders: number;
  revenue: string;
  average_order_value: string;
  orders_by_status: Record<string, number>;
  orders_by_hour: HourMetric[];
}

export interface ForecastItem {
  date: string;
  predicted_orders: number;
}

export interface AssistantAnswer {
  answer: string;
  sources: string[];
}

export interface AccessToken {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

export interface CurrentAccount {
  username: string;
  restaurant_id: string;
}
