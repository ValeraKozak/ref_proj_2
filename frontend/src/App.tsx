import { useEffect, useMemo, useState } from "react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { Header } from "./components/Header";
import { APIError, api } from "./lib/api";
import type { Category, Health, Listing, Message, User } from "./lib/types";
import { CatalogPage } from "./pages/CatalogPage";
import { ErrorPage } from "./pages/ErrorPage";
import { HomePage } from "./pages/HomePage";
import { ListingDetailPage } from "./pages/ListingDetailPage";
import { WorkspacePage } from "./pages/WorkspacePage";

const TOKEN_KEY = "bulletin-board-token";

function resolvePageError(error: unknown): number | null {
  if (!(error instanceof APIError)) {
    return null;
  }
  if (error.status >= 500) {
    return 500;
  }
  if (error.status === 400) {
    return 400;
  }
  return null;
}

export function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [health, setHealth] = useState<Health | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [listings, setListings] = useState<Listing[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [myListings, setMyListings] = useState<Listing[]>([]);
  const [pendingListings, setPendingListings] = useState<Listing[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [token, setToken] = useState<string>(() => window.localStorage.getItem(TOKEN_KEY) ?? "");

  function navigateToError(error: unknown) {
    console.error(error);
    const code = resolvePageError(error);
    if (code) {
      navigate(`/errors/${code}`, { replace: true });
    }
  }

  function clearPrivateState() {
    setUser(null);
    setMyListings([]);
    setPendingListings([]);
    setMessages([]);
  }

  function clearToken() {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken("");
  }

  function ensureToken() {
    if (!token) {
      throw new Error("Login required");
    }
    return token;
  }

  function updateModerationQueue(activeUser: User, queue: Listing[]) {
    if (activeUser.role === "moderator" || activeUser.role === "admin") {
      setPendingListings(queue);
      return;
    }
    setPendingListings([]);
  }

  async function loadPendingListingsForRole(activeToken: string, activeUser: User) {
    if (activeUser.role !== "moderator" && activeUser.role !== "admin") {
      return [];
    }
    return api.pendingListings(activeToken);
  }

  async function refreshPublicData() {
    const [healthData, categoryData, listingData] = await Promise.all([
      api.health(),
      api.categories(),
      api.listings(),
    ]);
    setHealth(healthData);
    setCategories(categoryData);
    setListings(listingData);
  }

  async function refreshPrivateData(activeToken: string) {
    const profile = await api.me(activeToken);
    setUser(profile);

    const [owned, inbox, queue] = await Promise.all([
      api.myListings(activeToken),
      api.messages(activeToken),
      loadPendingListingsForRole(activeToken, profile),
    ]);
    setMyListings(owned);
    setMessages(inbox);
    updateModerationQueue(profile, queue);
  }

  useEffect(() => {
    refreshPublicData().catch(navigateToError);
  }, [navigate]);

  useEffect(() => {
    if (!token) {
      clearPrivateState();
      return;
    }

    refreshPrivateData(token).catch((error) => {
      if (error instanceof APIError && (error.status === 401 || error.status === 403)) {
        clearToken();
        return;
      }
      navigateToError(error);
    });
  }, [navigate, token]);

  async function handleLogin(email: string, password: string) {
    const result = await api.login(email, password);
    window.localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
  }

  async function handleRegister(email: string, fullName: string, password: string) {
    await api.register(email, fullName, password);
    await handleLogin(email, password);
  }

  async function handleCreateListing(payload: {
    title: string;
    description: string;
    price: number;
    category_id: number;
    image_urls: string[];
  }) {
    const activeToken = ensureToken();
    await api.createListing(activeToken, payload);
    await Promise.all([refreshPublicData(), refreshPrivateData(activeToken)]);
  }

  async function handleUploadImages(files: File[]) {
    return api.uploadImages(ensureToken(), files);
  }

  async function handleCreateCategory(payload: { name: string; description: string }) {
    const activeToken = ensureToken();
    await api.createCategory(activeToken, payload);
    await refreshPublicData();
    await refreshPrivateData(activeToken);
  }

  async function handleModerateListing(
    listing_id: number,
    payload: { approved: boolean; rejection_reason?: string | null },
  ) {
    const activeToken = ensureToken();
    await api.moderateListing(activeToken, listing_id, payload);
    await Promise.all([refreshPublicData(), refreshPrivateData(activeToken)]);
  }

  async function handleSendMessage(payload: {
    listing_id: number;
    recipient_id: number;
    body: string;
  }) {
    const activeToken = ensureToken();
    await api.sendMessage(activeToken, payload);
    await refreshPrivateData(activeToken);
  }

  const isAuthenticated = useMemo(() => Boolean(token && user), [token, user]);
  const isErrorRoute = location.pathname.startsWith("/errors/");

  return (
    <div className={`app-shell${isErrorRoute ? " app-shell--error" : ""}`}>
      {isErrorRoute ? null : <Header isAuthenticated={isAuthenticated} userName={user?.full_name} />}
      <main>
        <Routes>
          <Route path="/" element={<HomePage health={health} categories={categories} listings={listings} />} />
          <Route path="/catalog" element={<CatalogPage categories={categories} />} />
          <Route
            path="/catalog/:listingId"
            element={
              <ListingDetailPage
                categories={categories}
                listings={listings}
                messages={messages}
                onSendMessage={handleSendMessage}
                token={token}
                user={user}
              />
            }
          />
          <Route
            path="/workspace"
            element={
              <WorkspacePage
                categories={categories}
                messages={messages}
                myListings={myListings}
                onCreateCategory={handleCreateCategory}
                onCreateListing={handleCreateListing}
                onLogin={handleLogin}
                onModerateListing={handleModerateListing}
                onRegister={handleRegister}
                pendingListings={pendingListings}
                user={user}
              />
            }
          />
          <Route path="/errors/:code" element={<ErrorPage />} />
          <Route path="*" element={<ErrorPage code={404} />} />
        </Routes>
      </main>
    </div>
  );
}
