import { FormEvent, useMemo, useState } from "react";

import type { Category, Listing, Message, User } from "../lib/types";
import { ListingCard } from "./ListingCard";

interface WorkspacePanelsProps {
  user: User | null;
  categories: Category[];
  myListings: Listing[];
  pendingListings: Listing[];
  messages: Message[];
  onCreateListing: (payload: {
    title: string;
    description: string;
    price: number;
    category_id: number;
    image_urls: string[];
  }) => Promise<void>;
  onCreateCategory: (payload: { name: string; description: string }) => Promise<void>;
  onModerateListing: (
    listing_id: number,
    payload: { approved: boolean; rejection_reason?: string | null },
  ) => Promise<void>;
}

type ListingFormState = {
  title: string;
  description: string;
  price: string;
  category_id: string;
  image_urls: string;
};

const EMPTY_LISTING_FORM: ListingFormState = {
  title: "",
  description: "",
  price: "",
  category_id: "",
  image_urls: "",
};

const LISTING_SUCCESS_MESSAGE = "Оголошення створено та відправлено на модерацію.";
const LISTING_FALLBACK_ERROR = "Не вдалося створити оголошення.";

export function WorkspacePanels({
  user,
  categories,
  myListings,
  pendingListings,
  messages,
  onCreateListing,
  onCreateCategory,
  onModerateListing,
}: WorkspacePanelsProps) {
  const canOperate = user?.role === "admin" || user?.role === "moderator";
  const categoryMap = useMemo(
    () => new Map(categories.map((category) => [category.id, category])),
    [categories],
  );

  const [listingForm, setListingForm] = useState<ListingFormState>(EMPTY_LISTING_FORM);
  const [categoryForm, setCategoryForm] = useState({ name: "", description: "" });
  const [moderationNotes, setModerationNotes] = useState<Record<number, string>>({});
  const [listingBusy, setListingBusy] = useState(false);
  const [categoryBusy, setCategoryBusy] = useState(false);
  const [moderationBusyId, setModerationBusyId] = useState<number | null>(null);
  const [listingError, setListingError] = useState("");
  const [categoryError, setCategoryError] = useState("");
  const [moderationError, setModerationError] = useState("");
  const [listingSuccess, setListingSuccess] = useState("");
  const [categorySuccess, setCategorySuccess] = useState("");
  const [moderationSuccess, setModerationSuccess] = useState("");

  function isValidHttpUrl(value: string) {
    try {
      const url = new URL(value);
      return url.protocol === "http:" || url.protocol === "https:";
    } catch {
      return false;
    }
  }

  function parseImageUrls(rawValue: string) {
    return rawValue
      .split("\n")
      .map((value) => value.trim())
      .filter(Boolean);
  }

  function getListingValidationError(
    currentUser: User | null,
    form: ListingFormState,
    imageUrls: string[],
  ) {
    if (!currentUser) {
      return "Увійдіть у систему, щоб створити оголошення.";
    }
    if (form.title.trim().length < 5) {
      return "Назва оголошення має містити щонайменше 5 символів.";
    }
    if (form.description.trim().length < 20) {
      return "Опис оголошення має містити щонайменше 20 символів.";
    }
    if (!form.price || Number(form.price) <= 0) {
      return "Вкажіть коректну ціну, більшу за 0.";
    }
    if (!form.category_id) {
      return "Оберіть категорію для оголошення.";
    }
    if (imageUrls.some((value) => !isValidHttpUrl(value))) {
      return "У полі зображень можна вказувати лише повні посилання формату http/https, по одному в рядку.";
    }
    return null;
  }

  function buildListingPayload(form: ListingFormState, imageUrls: string[]) {
    return {
      title: form.title.trim(),
      description: form.description.trim(),
      price: Number(form.price),
      category_id: Number(form.category_id),
      image_urls: imageUrls,
    };
  }

  async function submitListing(event: FormEvent) {
    event.preventDefault();
    setListingError("");
    setListingSuccess("");

    const imageUrls = parseImageUrls(listingForm.image_urls);
    const validationError = getListingValidationError(user, listingForm, imageUrls);
    if (validationError) {
      setListingError(validationError);
      return;
    }

    setListingBusy(true);

    try {
      await onCreateListing(buildListingPayload(listingForm, imageUrls));
      setListingForm(EMPTY_LISTING_FORM);
      setListingSuccess(LISTING_SUCCESS_MESSAGE);
    } catch (error) {
      setListingError(error instanceof Error ? error.message : LISTING_FALLBACK_ERROR);
    } finally {
      setListingBusy(false);
    }
  }

  async function submitCategory(event: FormEvent) {
    event.preventDefault();
    setCategoryError("");
    setCategorySuccess("");

    if (!canOperate) {
      setCategoryError("Створювати категорії можуть лише адміністратор або модератор.");
      return;
    }
    if (categoryForm.name.trim().length < 2) {
      setCategoryError("Назва категорії має містити щонайменше 2 символи.");
      return;
    }
    if (categoryForm.description.trim().length < 5) {
      setCategoryError("Опис категорії має містити щонайменше 5 символів.");
      return;
    }

    setCategoryBusy(true);

    try {
      await onCreateCategory({
        name: categoryForm.name.trim(),
        description: categoryForm.description.trim(),
      });
      setCategoryForm({ name: "", description: "" });
      setCategorySuccess("Категорію успішно створено.");
    } catch (error) {
      setCategoryError(error instanceof Error ? error.message : "Не вдалося створити категорію.");
    } finally {
      setCategoryBusy(false);
    }
  }

  async function moderateListing(listingId: number, approved: boolean) {
    setModerationError("");
    setModerationSuccess("");

    const note = moderationNotes[listingId]?.trim() ?? "";
    if (!approved && note.length < 5) {
      setModerationError("Для відхилення вкажіть коротку причину щонайменше з 5 символів.");
      return;
    }

    setModerationBusyId(listingId);
    try {
      await onModerateListing(listingId, {
        approved,
        rejection_reason: approved ? null : note,
      });
      setModerationNotes((current) => {
        const next = { ...current };
        delete next[listingId];
        return next;
      });
      setModerationSuccess(
        approved
          ? "Оголошення схвалено і воно вже може з'являтися в каталозі."
          : "Оголошення відхилено з поясненням для автора.",
      );
    } catch (error) {
      setModerationError(
        error instanceof Error ? error.message : "Не вдалося завершити модерацію.",
      );
    } finally {
      setModerationBusyId(null);
    }
  }

  return (
    <div className="workspace-grid">
      <section className="workspace-panel">
        <div className="workspace-panel__header">
          <span className="eyebrow">Публікація</span>
          <h3>{user ? `Робоча зона ${user.full_name}` : "Попередній перегляд кабінету"}</h3>
        </div>
        <form className="stack-form" onSubmit={submitListing}>
          <label>
            Назва оголошення
            <input
              value={listingForm.title}
              onChange={(event) =>
                setListingForm((current) => ({ ...current, title: event.target.value }))
              }
            />
          </label>
          <label>
            Опис
            <textarea
              value={listingForm.description}
              onChange={(event) =>
                setListingForm((current) => ({ ...current, description: event.target.value }))
              }
            />
          </label>
          <div className="form-row">
            <label>
              Ціна
              <input
                type="number"
                min="1"
                step="0.01"
                value={listingForm.price}
                onChange={(event) =>
                  setListingForm((current) => ({ ...current, price: event.target.value }))
                }
              />
            </label>
            <label>
              Категорія
              <select
                value={listingForm.category_id}
                onChange={(event) =>
                  setListingForm((current) => ({ ...current, category_id: event.target.value }))
                }
              >
                <option value="">Оберіть категорію</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            Посилання на зображення
            <textarea
              value={listingForm.image_urls}
              placeholder="Необов'язково. Вкажіть повні http/https URL, по одному в рядку."
              onChange={(event) =>
                setListingForm((current) => ({ ...current, image_urls: event.target.value }))
              }
            />
          </label>
          <button className="cta-button" disabled={listingBusy} type="submit">
            {listingBusy ? "Публікуємо..." : "Опублікувати оголошення"}
          </button>
          {listingError ? <p className="form-error">{listingError}</p> : null}
          {listingSuccess ? <p className="form-success">{listingSuccess}</p> : null}
        </form>
      </section>

      {canOperate ? (
        <section className="workspace-panel subtle">
          <div className="workspace-panel__header">
            <span className="eyebrow">Операційна панель</span>
            <h3>Модерація, категорії та повідомлення</h3>
          </div>
          <div className="mini-stats">
            <div>
              <strong>{pendingListings.length}</strong>
              <span>Чекають модерації</span>
            </div>
            <div>
              <strong>{messages.length}</strong>
              <span>Повідомлення</span>
            </div>
            <div>
              <strong>{myListings.length}</strong>
              <span>Мої оголошення</span>
            </div>
          </div>
          <form className="stack-form compact" onSubmit={submitCategory}>
            <label>
              Нова категорія
              <input
                value={categoryForm.name}
                onChange={(event) =>
                  setCategoryForm((current) => ({ ...current, name: event.target.value }))
                }
              />
            </label>
            <label>
              Опис категорії
              <input
                value={categoryForm.description}
                onChange={(event) =>
                  setCategoryForm((current) => ({ ...current, description: event.target.value }))
                }
              />
            </label>
            <button className="ghost-button" disabled={categoryBusy} type="submit">
              {categoryBusy ? "Створюємо..." : "Додати категорію"}
            </button>
            {categoryError ? <p className="form-error">{categoryError}</p> : null}
            {categorySuccess ? <p className="form-success">{categorySuccess}</p> : null}
          </form>

          <section className="moderation-board">
            <div className="moderation-board__header">
              <div>
                <strong>Черга модерації</strong>
                <p>
                  Швидко переглядайте pending-оголошення, схвалюйте якісні публікації або
                  повертайте їх автору з поясненням.
                </p>
              </div>
              <span className="status-pill">{pendingListings.length} у черзі</span>
            </div>

            {moderationError ? <p className="form-error">{moderationError}</p> : null}
            {moderationSuccess ? <p className="form-success">{moderationSuccess}</p> : null}

            <div className="moderation-grid">
              {pendingListings.length ? (
                pendingListings.map((listing) => (
                  <article className="moderation-card" key={listing.id}>
                    <div className="moderation-card__top">
                      <div>
                        <span className="eyebrow">Pending review</span>
                        <h4>{listing.title}</h4>
                      </div>
                      <span className="status-badge pending">Pending</span>
                    </div>

                    <div className="moderation-card__meta">
                      <span>{categoryMap.get(listing.category_id)?.name ?? "Без категорії"}</span>
                      <strong>${listing.price.toFixed(2)}</strong>
                    </div>

                    <p className="moderation-card__description">{listing.description}</p>

                    <label className="moderation-card__label">
                      Причина відхилення
                      <textarea
                        value={moderationNotes[listing.id] ?? ""}
                        placeholder="Наприклад: потрібні чіткіші фото, уточніть стан товару або заповніть опис."
                        onChange={(event) =>
                          setModerationNotes((current) => ({
                            ...current,
                            [listing.id]: event.target.value,
                          }))
                        }
                      />
                    </label>

                    <div className="moderation-card__actions">
                      <button
                        className="ghost-button moderation-card__approve"
                        disabled={moderationBusyId === listing.id}
                        type="button"
                        onClick={() => void moderateListing(listing.id, true)}
                      >
                        {moderationBusyId === listing.id ? "Обробляємо..." : "Схвалити"}
                      </button>
                      <button
                        className="cta-button moderation-card__reject"
                        disabled={moderationBusyId === listing.id}
                        type="button"
                        onClick={() => void moderateListing(listing.id, false)}
                      >
                        {moderationBusyId === listing.id ? "Обробляємо..." : "Відхилити"}
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-card moderation-empty">
                  <strong>Черга чиста</strong>
                  <p>
                    Наразі немає pending-оголошень. Нові публікації з&apos;являються тут
                    автоматично.
                  </p>
                </div>
              )}
            </div>
          </section>

          <div className="workspace-list-preview">
            <div>
              <strong>Останні повідомлення</strong>
              <ul>
                {messages.length ? (
                  messages.slice(0, 3).map((message) => <li key={message.id}>{message.body}</li>)
                ) : (
                  <li>Поки що повідомлень немає.</li>
                )}
              </ul>
            </div>
            <div>
              <strong>Що перевіряти насамперед</strong>
              <ul>
                <li>Чи достатньо конкретний заголовок.</li>
                <li>Чи опис дає покупцю повну картину.</li>
                <li>Чи є адекватна ціна та коректна категорія.</li>
              </ul>
            </div>
          </div>
        </section>
      ) : null}

      <section className="workspace-panel wide">
        <div className="workspace-panel__header">
          <span className="eyebrow">Асортимент</span>
          <h3>Ваші поточні оголошення</h3>
        </div>
        <div className="listing-grid compact">
          {myListings.length ? (
            myListings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                category={categoryMap.get(listing.category_id)}
              />
            ))
          ) : (
            <div className="empty-card">
              <strong>Поки що немає жодного оголошення</strong>
              <p>
                Створіть першу публікацію у верхній формі, і вона одразу з&apos;явиться тут.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
