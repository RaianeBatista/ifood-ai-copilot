import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import {
  askAssistant,
  clearAccessToken,
  getCurrentAccount,
  getForecast,
  getOrders,
  getSummary,
  hasAccessToken,
  login,
  storeAccessToken,
} from "./api";
import type {
  CurrentAccount,
  AssistantAnswer,
  ForecastItem,
  OperationalSummary,
  Order,
  OrderStatus,
} from "./types";

const currency = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});
const number = new Intl.NumberFormat("pt-BR");
const dateTime = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
});
const shortDate = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
});

const statusLabels: Record<OrderStatus, string> = {
  pending: "Pendente",
  preparing: "Em preparo",
  delivered: "Entregue",
  cancelled: "Cancelado",
};

interface ChatTurn {
  id: string;
  question: string;
  answer?: AssistantAnswer;
  error?: string;
  pending: boolean;
}

interface LoginPageProps {
  error: string;
  isSubmitting: boolean;
  onSubmit: (username: string, password: string) => Promise<void>;
}

function LoginPage({ error, isSubmitting, onSubmit }: LoginPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(username.trim(), password);
  }

  return (
    <main className="auth-page">
      <section className="login-card" aria-labelledby="login-title">
        <a className="brand login-brand" href="/" aria-label="iFood AI Copilot">
          <span className="brand-name">iFood</span>
          <span className="brand-divider" />
          <span className="brand-product">AI Copilot</span>
        </a>
        <p className="eyebrow">ACESSO DE TESTE</p>
        <h1 id="login-title">Bem-vindo ao seu painel</h1>
        <p className="login-description">
          Entre com o e-mail e a senha compartilhados para testar o protótipo.
        </p>
        <form className="login-form" onSubmit={(event) => void handleSubmit(event)}>
          <label>
            E-mail
            <input
              autoComplete="email"
              maxLength={100}
              onChange={(event) => setUsername(event.target.value)}
              required
              type="email"
              value={username}
            />
          </label>
          <label>
            Senha
            <span className="password-field">
              <input
                autoComplete="current-password"
                onChange={(event) => setPassword(event.target.value)}
                required
                type={showPassword ? "text" : "password"}
                value={password}
              />
              <button
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                aria-pressed={showPassword}
                className="password-visibility"
                onClick={() => setShowPassword((visible) => !visible)}
                type="button"
              >
                {showPassword ? (
                  <svg aria-hidden="true" viewBox="0 0 24 24">
                    <path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8" />
                    <path d="M9.9 5.2A10.8 10.8 0 0112 5c5.5 0 9 7 9 7a15.7 15.7 0 01-3 3.8M6.2 6.2C3.9 7.8 3 12 3 12s3.5 7 9 7a9.5 9.5 0 004.1-.9" />
                  </svg>
                ) : (
                  <svg aria-hidden="true" viewBox="0 0 24 24">
                    <path d="M3 12s3.5-7 9-7 9 7 9 7-3.5 7-9 7-9-7-9-7z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                )}
              </button>
            </span>
          </label>
          {error && <p className="login-error" role="alert">{error}</p>}
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Entrando…" : "Entrar"}
            <span aria-hidden="true">→</span>
          </button>
        </form>
        <p className="login-note">
          Esta conta de demonstração dá acesso ao mesmo restaurante de teste.
        </p>
      </section>
    </main>
  );
}

function App() {
  const [account, setAccount] = useState<CurrentAccount | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [loginSubmitting, setLoginSubmitting] = useState(false);
  const [preparingDashboard, setPreparingDashboard] = useState(false);
  const [logoutSubmitting, setLogoutSubmitting] = useState(false);
  const [restaurantId, setRestaurantId] = useState("");
  const [period, setPeriod] = useState(30);
  const [summary, setSummary] = useState<OperationalSummary | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [forecast, setForecast] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [forecastError, setForecastError] = useState("");
  const [question, setQuestion] = useState("");
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([]);
  const [assistantError, setAssistantError] = useState("");
  const [asking, setAsking] = useState(false);
  const conversationEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleSessionExpired() {
      setAccount(null);
      setRestaurantId("");
      setLoginError("Sua sessão expirou. Entre novamente para continuar.");
    }

    window.addEventListener("auth-expired", handleSessionExpired);
    let active = true;
    async function restoreSession() {
      if (!hasAccessToken()) {
        setAuthReady(true);
        return;
      }

      try {
        const currentAccount = await getCurrentAccount();
        if (active) {
          setAccount(currentAccount);
          setRestaurantId(currentAccount.restaurant_id);
        }
      } catch (restoreError) {
        if (active) {
          setLoginError(
            restoreError instanceof Error
              ? `Não foi possível restaurar a sessão: ${restoreError.message}`
              : "Não foi possível restaurar a sessão.",
          );
        }
      } finally {
        if (active) {
          setAuthReady(true);
        }
      }
    }

    void restoreSession();
    return () => {
      active = false;
      window.removeEventListener("auth-expired", handleSessionExpired);
    };
  }, []);

  async function handleLogin(username: string, password: string) {
    setLoginSubmitting(true);
    setLoginError("");
    try {
      const token = await login(username, password);
      storeAccessToken(token.access_token);
      const currentAccount = await getCurrentAccount();
      setPreparingDashboard(true);
      await new Promise((resolve) => window.setTimeout(resolve, 1600));
      setAccount(currentAccount);
      setRestaurantId(currentAccount.restaurant_id);
      setPreparingDashboard(false);
    } catch (loginRequestError) {
      clearAccessToken();
      setPreparingDashboard(false);
      setLoginError(
        loginRequestError instanceof Error
          ? loginRequestError.message
          : "Não foi possível entrar. Tente novamente.",
      );
    } finally {
      setLoginSubmitting(false);
    }
  }

  async function handleLogout() {
    if (logoutSubmitting) {
      return;
    }

    setLogoutSubmitting(true);
    clearAccessToken();
    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 800);
    });
    setAccount(null);
    setRestaurantId("");
    setSummary(null);
    setOrders([]);
    setForecast([]);
    setChatTurns([]);
    setLoginError("");
    setLogoutSubmitting(false);
  }

  const loadDashboard = useCallback(async () => {
    if (!account) {
      return;
    }
    const selectedRestaurant = restaurantId.trim();
    if (!selectedRestaurant) {
      setError("Informe o identificador do restaurante.");
      return;
    }

    setLoading(true);
    setError("");
    setForecastError("");

    try {
      const [summaryResult, ordersResult, forecastResult] =
        await Promise.allSettled([
          getSummary(selectedRestaurant, period),
          getOrders(selectedRestaurant),
          getForecast(selectedRestaurant),
        ]);

      if (summaryResult.status === "rejected") {
        throw summaryResult.reason;
      }
      if (ordersResult.status === "rejected") {
        throw ordersResult.reason;
      }

      setSummary(summaryResult.value);
      setOrders(ordersResult.value);

      if (forecastResult.status === "fulfilled") {
        setForecast(forecastResult.value);
      } else {
        setForecast([]);
        setForecastError(
          forecastResult.reason instanceof Error
            ? forecastResult.reason.message
            : "Não foi possível carregar a previsão.",
        );
      }
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Não foi possível carregar os dados do dashboard.",
      );
    } finally {
      setLoading(false);
    }
  }, [account, period, restaurantId]);

  useEffect(() => {
    if (account) {
      void loadDashboard();
    }
  }, [account, loadDashboard]);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }, [chatTurns]);

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (asking || !account) {
      return;
    }

    const selectedRestaurant = restaurantId.trim();
    const prompt = question.trim();
    if (!selectedRestaurant || prompt.length < 3) {
      setAssistantError("Digite uma pergunta com pelo menos 3 caracteres.");
      return;
    }

    const turnId = `${Date.now()}-${chatTurns.length}`;
    setQuestion("");
    setAsking(true);
    setAssistantError("");
    setChatTurns((turns) => [
      ...turns,
      { id: turnId, question: prompt, pending: true },
    ]);

    try {
      const result = await askAssistant(selectedRestaurant, prompt);
      setChatTurns((turns) =>
        turns.map((turn) =>
          turn.id === turnId ? { ...turn, answer: result, pending: false } : turn,
        ),
      );
    } catch (askError) {
      const message =
        askError instanceof Error
          ? askError.message
          : "Não foi possível consultar o assistente.";
      setChatTurns((turns) =>
        turns.map((turn) =>
          turn.id === turnId ? { ...turn, error: message, pending: false } : turn,
        ),
      );
    } finally {
      setAsking(false);
    }
  }

  const cancellationRate =
    summary && summary.total_orders > 0
      ? (summary.cancelled_orders / summary.total_orders) * 100
      : 0;
  const maxHourOrders = Math.max(
    1,
    ...(summary?.orders_by_hour.map((item) => item.orders) ?? []),
  );
  const maxForecast = Math.max(
    1,
    ...forecast.map((item) => item.predicted_orders),
  );

  if (!authReady) {
    return (
      <main className="auth-page">
        <p role="status">Verificando sua sessão…</p>
      </main>
    );
  }

  if (preparingDashboard) {
    return (
      <main className="auth-page">
        <section className="dashboard-loading" role="status" aria-live="polite">
          <a className="brand login-brand" href="/" aria-label="iFood AI Copilot">
            <span className="brand-name">iFood</span>
            <span className="brand-divider" />
            <span className="brand-product">AI Copilot</span>
          </a>
          <span className="loading-spinner" aria-hidden="true" />
          <h1>Preparando seu painel</h1>
          <p>Estamos organizando os dados do seu restaurante…</p>
        </section>
      </main>
    );
  }

  if (!account) {
    return (
      <LoginPage
        error={loginError}
        isSubmitting={loginSubmitting}
        onSubmit={handleLogin}
      />
    );
  }

  return (
    <div className="app-shell">
      <div className="utility-bar">
        <a href="#main">Ir para o conteúdo</a>
        <span>Projeto independente · iFood AI Copilot</span>
      </div>

      <aside className="sidebar">
        <a className="brand" href="#main" aria-label="iFood AI Copilot, início">
          <span className="brand-name">iFood</span>
          <span className="brand-divider" />
          <span className="brand-product">AI Copilot</span>
        </a>
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <div className="nav-group">
            <p className="sidebar-label">OPERAÇÃO</p>
            <a className="nav-link active" href="#overview">
              <span aria-hidden="true">⌂</span>Visão geral
            </a>
            <a className="nav-link" href="#orders">
              <span aria-hidden="true">≡</span>Pedidos
            </a>
            <a className="nav-link" href="#assistant">
              <span aria-hidden="true">✳</span>Assistente IA
            </a>
          </div>
          <div className="nav-group">
            <p className="sidebar-label">FINANCEIRO</p>
            <a className="nav-link" href="#cash-flow">
              <span aria-hidden="true">↗</span>Fluxo de caixa
            </a>
            <a className="nav-link" href="#business-score">
              <span aria-hidden="true">◉</span>Score do negócio
            </a>
            <a className="nav-link" href="#credit">
              <span aria-hidden="true">＋</span>Solicitar crédito
              <small>Em breve</small>
            </a>
            <a className="nav-link" href="#investments">
              <span aria-hidden="true">◇</span>Investimentos
              <small>Em breve</small>
            </a>
          </div>
        </nav>
        <div className="sidebar-agent">
          <span className="agent-avatar">P</span>
          <span><strong>Prato</strong><small>Seu copiloto IA</small></span>
        </div>
      </aside>

      <div className="workspace">
        <header className="site-header">
          <div className="breadcrumb">
            iFood AI Copilot <span>/</span> Painel do restaurante
          </div>
          <div className="header-actions">
            <span className="account-name">{account.username}</span>
            <button
              className="logout-action"
              type="button"
              onClick={() => void handleLogout()}
              disabled={logoutSubmitting}
            >
              {logoutSubmitting ? "Saindo…" : "Sair"}
            </button>
            <button
              className="header-action"
              type="button"
              onClick={() => void loadDashboard()}
              disabled={loading}
            >
              {loading ? "Atualizando…" : "Atualizar dados"}
              <span aria-hidden="true">↗</span>
            </button>
          </div>
        </header>

        <main id="main">
        <section className="hero" id="overview">
          <div className="hero-shape hero-shape-one" />
          <div className="hero-shape hero-shape-two" />
          <div className="hero-inner">
            <div className="hero-copy">
              <p className="hero-kicker">PAINEL DO RESTAURANTE</p>
              <h1>Sua operação.<br />Em outro nível.</h1>
              <p className="hero-description">
                Indicadores e inteligência para você tomar decisões com mais confiança.
              </p>
            </div>
            <div className="hero-aside" aria-hidden="true">
              <span className="hero-orbit orbit-one" />
              <span className="hero-orbit orbit-two" />
              <div className="hero-insight">
                <span className="insight-spark">✳</span>
                <span>Dados que<br /><strong>movem sua operação</strong></span>
                <span className="insight-arrow">↗</span>
              </div>
            </div>
            <form
              className="hero-filters"
              onSubmit={(event) => {
                event.preventDefault();
                void loadDashboard();
              }}
            >
              <label className="filter-field restaurant-filter">
                <span>Restaurante da conta</span>
                <input
                  aria-label="Identificador do restaurante"
                  readOnly
                  value={restaurantId}
                />
              </label>
              <label className="filter-field">
                <span>Período dos indicadores</span>
                <select
                  aria-label="Período dos indicadores"
                  value={period}
                  onChange={(event) => setPeriod(Number(event.target.value))}
                >
                  <option value={7}>7 dias</option>
                  <option value={30}>30 dias</option>
                  <option value={90}>90 dias</option>
                </select>
              </label>
              <button className="search-button" type="submit" disabled={loading}>
                {loading ? "Carregando…" : "Ver meus indicadores"}
                <span aria-hidden="true">→</span>
              </button>
            </form>
          </div>
        </section>

        <div className="page-content">
          {error && (
            <div className="error-banner" role="alert">
              <strong>Não foi possível carregar os dados.</strong>
              <span>{error}</span>
              <button type="button" onClick={() => void loadDashboard()}>Tentar novamente</button>
            </div>
          )}

          <section className="metrics-section" aria-label="Indicadores principais">
            <div className="section-heading">
              <div>
                <p className="eyebrow">SEU RESTAURANTE EM NÚMEROS</p>
                <h2>Um panorama da sua operação</h2>
              </div>
              <span className="period-label">Últimos {period} dias</span>
            </div>
            <div className="metrics-grid">
              <MetricCard
                label="Pedidos no período"
                value={summary ? number.format(summary.total_orders) : "—"}
                note="Todos os status"
                icon="≡"
                loading={loading && !summary}
              />
              <MetricCard
                label="Faturamento"
                value={summary ? currency.format(Number(summary.revenue)) : "—"}
                note="Pedidos entregues"
                icon="R$"
                loading={loading && !summary}
              />
              <MetricCard
                label="Ticket médio"
                value={summary ? currency.format(Number(summary.average_order_value)) : "—"}
                note="Por pedido entregue"
                icon="↗"
                loading={loading && !summary}
              />
              <MetricCard
                label="Cancelamentos"
                value={summary ? `${cancellationRate.toFixed(1).replace(".", ",")}%` : "—"}
                note={`${number.format(summary?.cancelled_orders ?? 0)} pedidos`}
                icon="%"
                loading={loading && !summary}
              />
            </div>
          </section>

          <section className="analysis-grid" aria-label="Análise da operação">
            <article className="panel hourly-panel" id="hourly">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">MOVIMENTO</p>
                  <h2>Quando seus clientes pedem?</h2>
                </div>
                <span className="panel-icon" aria-hidden="true">◷</span>
              </div>
              {summary && summary.total_orders > 0 ? (
                <div className="hour-chart" role="img" aria-label="Gráfico de pedidos por hora">
                  {summary.orders_by_hour.map((item) => {
                    const height =
                      item.orders === 0
                        ? 3
                        : Math.max(12, (item.orders / maxHourOrders) * 100);
                    return (
                      <div className="hour-column" key={item.hour}>
                        <span className="bar-value">
                          {item.orders > 0 ? item.orders : ""}
                        </span>
                        <div className="bar-track">
                          <div
                            className={`hour-bar ${item.orders === maxHourOrders ? "peak" : ""}`}
                            style={{ height: `${height}%` }}
                          />
                        </div>
                        <span className={`hour-label ${item.hour % 3 !== 0 ? "muted" : ""}`}>
                          {item.hour % 3 === 0 ? `${String(item.hour).padStart(2, "0")}h` : "·"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <EmptyState
                  title="Ainda sem movimento"
                  description="Os pedidos deste restaurante aparecerão aqui."
                />
              )}
              <div className="chart-footnote">
                <span className="legend-dot" /> Pedidos não cancelados
              </div>
            </article>

            <article className="panel forecast-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">MACHINE LEARNING</p>
                  <h2>O que vem pela frente</h2>
                </div>
                <span className="panel-icon panel-icon-red" aria-hidden="true">↗</span>
              </div>
              <p className="panel-description">
                Estimativa de pedidos para os próximos 7 dias.
              </p>
              {forecastError ? (
                <div className="inline-notice">
                  <strong>Previsão indisponível</strong>
                  <span>{forecastError}</span>
                </div>
              ) : forecast.length > 0 ? (
                <div className="forecast-list">
                  {forecast.map((item, index) => (
                    <div className="forecast-row" key={item.date}>
                      <span className="forecast-date">
                        {index === 0 ? "Amanhã" : shortDate.format(new Date(`${item.date}T12:00:00`))}
                      </span>
                      <div className="forecast-track">
                        <div
                          className="forecast-bar"
                          style={{
                            width: `${Math.max(4, (item.predicted_orders / maxForecast) * 100)}%`,
                          }}
                        />
                      </div>
                      <strong>{number.format(item.predicted_orders)}</strong>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title={loading ? "Calculando previsão…" : "Sem dados para prever"}
                  description="A previsão fica disponível quando há pedidos em pelo menos dois dias."
                />
              )}
              <div className="model-note">
                <span className="model-pulse" />
                Modelo de regressão linear
              </div>
            </article>
          </section>

          <section className="finance-section" id="finance">
            <div className="section-heading">
              <div>
                <p className="eyebrow">SOLUÇÕES PARA O SEU NEGÓCIO</p>
                <h2>Seu próximo passo financeiro</h2>
              </div>
            </div>
            <div className="finance-grid">
              <article className="finance-card cash-flow-card" id="cash-flow">
                <div className="finance-card-heading">
                  <span className="finance-icon" aria-hidden="true">↗</span>
                  <span className="feature-status">Estimativa</span>
                </div>
                <p className="finance-title">Fluxo de caixa</p>
                <strong className="finance-value">
                  {summary ? currency.format(Number(summary.revenue)) : "—"}
                </strong>
                <p className="finance-description">
                  Faturamento de pedidos entregues nos últimos {period} dias.
                </p>
                <p className="finance-disclaimer">
                  Estimativa bruta: não considera taxas, custos ou prazo de repasse.
                </p>
              </article>
              <article className="finance-card" id="business-score">
                <div className="finance-card-heading">
                  <span className="finance-icon" aria-hidden="true">◉</span>
                  <span className="feature-status coming-soon">Em breve</span>
                </div>
                <p className="finance-title">Score do negócio</p>
                <p className="finance-description">
                  Uma leitura transparente da saúde operacional, baseada no histórico
                  de pedidos e desempenho.
                </p>
              </article>
              <article className="finance-card" id="credit">
                <div className="finance-card-heading">
                  <span className="finance-icon" aria-hidden="true">＋</span>
                  <span className="feature-status coming-soon">Em breve</span>
                </div>
                <p className="finance-title">Solicitar crédito</p>
                <p className="finance-description">
                  Estamos planejando conectar merchants a parceiros financeiros.
                </p>
              </article>
              <article className="finance-card" id="investments">
                <div className="finance-card-heading">
                  <span className="finance-icon" aria-hidden="true">◇</span>
                  <span className="feature-status coming-soon">Em breve</span>
                </div>
                <p className="finance-title">Investimentos</p>
                <p className="finance-description">
                  Em breve: informações e soluções com parceiros especializados.
                </p>
              </article>
            </div>
          </section>

          <section className="orders-section" id="orders">
            <div className="section-heading">
              <div>
                <p className="eyebrow">ACOMPANHAMENTO</p>
                <h2>Pedidos recentes</h2>
              </div>
              <span className="count-label">{number.format(orders.length)} exibidos</span>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Pedido</th>
                    <th>Data e hora</th>
                    <th>Itens</th>
                    <th>Valor</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td className="order-id">#{order.id.slice(0, 8)}</td>
                      <td>{dateTime.format(new Date(order.created_at))}</td>
                      <td>{number.format(order.items_count)}</td>
                      <td className="order-amount">{currency.format(Number(order.amount))}</td>
                      <td>
                        <span className={`status-pill status-${order.status}`}>
                          <span />
                          {statusLabels[order.status]}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {orders.length === 0 && !loading && (
                <EmptyState
                  title="Nenhum pedido encontrado"
                  description="Confira o identificador ou cadastre pedidos pela API."
                />
              )}
            </div>
          </section>

          <section
            className={`assistant-section${chatTurns.length > 0 ? " has-messages" : ""}`}
            id="assistant"
          >
            <div className="assistant-copy">
              <span className="assistant-mark" aria-hidden="true">P</span>
              <div>
                <p className="eyebrow">SEU COPILOTO</p>
                <h2>Prato, seu copiloto de negócio.</h2>
                <p>Dados do seu restaurante, ideias práticas e ajuda com próximos passos.</p>
              </div>
            </div>
            {chatTurns.length > 0 && (
              <div className="conversation" aria-label="Histórico da conversa">
                {chatTurns.map((turn) => (
                  <article className="chat-turn" key={turn.id}>
                    <div className="user-message">
                      <span className="message-author">Você</span>
                      <p className="user-bubble">{turn.question}</p>
                    </div>
                    <div className="assistant-message" aria-live="polite">
                      <span className="message-author">Prato</span>
                      {turn.pending ? (
                        <p className="typing-indicator" role="status">
                          Analisando seus dados…
                        </p>
                      ) : turn.error ? (
                        <p className="message-error" role="alert">{turn.error}</p>
                      ) : turn.answer ? (
                        <>
                          <p>{turn.answer.answer}</p>
                          {turn.answer.sources.length > 0 && (
                            <div className="answer-sources">
                              <strong>Contexto usado</strong>
                              {turn.answer.sources.map((source, index) => (
                                <span key={`${index}-${source}`}>{source}</span>
                              ))}
                            </div>
                          )}
                        </>
                      ) : null}
                    </div>
                  </article>
                ))}
                <div ref={conversationEndRef} />
              </div>
            )}
            {assistantError && <p className="assistant-error" role="alert">{assistantError}</p>}
            <form className="assistant-form" onSubmit={handleAsk}>
              <label className="visually-hidden" htmlFor="assistant-question">
                Pergunta para o assistente
              </label>
              <input
                id="assistant-question"
                value={question}
                onChange={(event) => {
                  setQuestion(event.target.value);
                  setAssistantError("");
                }}
                placeholder="Ex.: Como posso criar uma campanha para meus clientes?"
              />
              <button type="submit" disabled={asking}>
                {asking ? "Analisando…" : "Perguntar"}
                <span aria-hidden="true">→</span>
              </button>
            </form>
          </section>
        </div>
        </main>

        <footer className="site-footer">
          <span>iFood AI Copilot</span>
          <span>Projeto independente para análise operacional</span>
        </footer>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  note,
  icon,
  loading,
}: {
  label: string;
  value: string;
  note: string;
  icon: string;
  loading: boolean;
}) {
  return (
    <article className="metric-card">
      <div className="metric-topline">
        <span className="metric-label">{label}</span>
        <span className="metric-icon" aria-hidden="true">{icon}</span>
      </div>
      <strong className={loading ? "metric-value skeleton" : "metric-value"}>{value}</strong>
      <span className="metric-note">{note}</span>
    </article>
  );
}

function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="empty-state">
      <span className="empty-mark" aria-hidden="true">—</span>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

export default App;
