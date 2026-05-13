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

const LISTING_SUCCESS_MESSAGE =
  "РћРіРѕР»РѕС€РµРЅРЅСЏ СЃС‚РІРѕСЂРµРЅРѕ С‚Р° РІС–РґРїСЂР°РІР»РµРЅРѕ РЅР° РјРѕРґРµСЂР°С†С–СЋ.";

const LISTING_FALLBACK_ERROR =
  "РќРµ РІРґР°Р»РѕСЃСЏ СЃС‚РІРѕСЂРёС‚Рё РѕРіРѕР»РѕС€РµРЅРЅСЏ.";

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
      return "РЈРІС–Р№РґС–С‚СЊ Сѓ СЃРёСЃС‚РµРјСѓ, С‰РѕР± СЃС‚РІРѕСЂРёС‚Рё РѕРіРѕР»РѕС€РµРЅРЅСЏ.";
    }
    if (form.title.trim().length < 5) {
      return "РќР°Р·РІР° РѕРіРѕР»РѕС€РµРЅРЅСЏ РјР°С” РјС–СЃС‚РёС‚Рё С‰РѕРЅР°Р№РјРµРЅС€Рµ 5 СЃРёРјРІРѕР»С–РІ.";
    }
    if (form.description.trim().length < 20) {
      return "РћРїРёСЃ РѕРіРѕР»РѕС€РµРЅРЅСЏ РјР°С” РјС–СЃС‚РёС‚Рё С‰РѕРЅР°Р№РјРµРЅС€Рµ 20 СЃРёРјРІРѕР»С–РІ.";
    }
    if (!form.price || Number(form.price) <= 0) {
      return "Р’РєР°Р¶С–С‚СЊ РєРѕСЂРµРєС‚РЅСѓ С†С–РЅСѓ, Р±С–Р»СЊС€Сѓ Р·Р° 0.";
    }
    if (!form.category_id) {
      return "РћР±РµСЂС–С‚СЊ РєР°С‚РµРіРѕСЂС–СЋ РґР»СЏ РѕРіРѕР»РѕС€РµРЅРЅСЏ.";
    }
    if (imageUrls.some((value) => !isValidHttpUrl(value))) {
      return "РЈ РїРѕР»С– Р·РѕР±СЂР°Р¶РµРЅСЊ РјРѕР¶РЅР° РІРєР°Р·СѓРІР°С‚Рё Р»РёС€Рµ РїРѕРІРЅС– РїРѕСЃРёР»Р°РЅРЅСЏ С„РѕСЂРјР°С‚Сѓ http/https, РїРѕ РѕРґРЅРѕРјСѓ РІ СЂСЏРґРєСѓ.";
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
      setCategoryError("РЎС‚РІРѕСЂСЋРІР°С‚Рё РєР°С‚РµРіРѕСЂС–С— РјРѕР¶СѓС‚СЊ Р»РёС€Рµ Р°РґРјС–РЅС–СЃС‚СЂР°С‚РѕСЂ Р°Р±Рѕ РјРѕРґРµСЂР°С‚РѕСЂ.");
      return;
    }
    if (categoryForm.name.trim().length < 2) {
      setCategoryError("РќР°Р·РІР° РєР°С‚РµРіРѕСЂС–С— РјР°С” РјС–СЃС‚РёС‚Рё С‰РѕРЅР°Р№РјРµРЅС€Рµ 2 СЃРёРјРІРѕР»Рё.");
      return;
    }
    if (categoryForm.description.trim().length < 5) {
      setCategoryError("РћРїРёСЃ РєР°С‚РµРіРѕСЂС–С— РјР°С” РјС–СЃС‚РёС‚Рё С‰РѕРЅР°Р№РјРµРЅС€Рµ 5 СЃРёРјРІРѕР»С–РІ.");
      return;
    }

    setCategoryBusy(true);

    try {
      await onCreateCategory({
        name: categoryForm.name.trim(),
        description: categoryForm.description.trim(),
      });
      setCategoryForm({ name: "", description: "" });
      setCategorySuccess("РљР°С‚РµРіРѕСЂС–СЋ СѓСЃРїС–С€РЅРѕ СЃС‚РІРѕСЂРµРЅРѕ.");
    } catch (error) {
      setCategoryError(error instanceof Error ? error.message : "РќРµ РІРґР°Р»РѕСЃСЏ СЃС‚РІРѕСЂРёС‚Рё РєР°С‚РµРіРѕСЂС–СЋ.");
    } finally {
      setCategoryBusy(false);
    }
  }

  async function moderateListing(listingId: number, approved: boolean) {
    setModerationError("");
    setModerationSuccess("");

    const note = moderationNotes[listingId]?.trim() ?? "";
    if (!approved && note.length < 5) {
      setModerationError("Р”Р»СЏ РІС–РґС…РёР»РµРЅРЅСЏ РІРєР°Р¶С–С‚СЊ РєРѕСЂРѕС‚РєСѓ РїСЂРёС‡РёРЅСѓ С‰РѕРЅР°Р№РјРµРЅС€Рµ Р· 5 СЃРёРјРІРѕР»С–РІ.");
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
          ? "РћРіРѕР»РѕС€РµРЅРЅСЏ СЃС…РІР°Р»РµРЅРѕ С– РІРѕРЅРѕ РІР¶Рµ РјРѕР¶Рµ Р·'СЏРІР»СЏС‚РёСЃСЏ РІ РєР°С‚Р°Р»РѕР·С–."
          : "РћРіРѕР»РѕС€РµРЅРЅСЏ РІС–РґС…РёР»РµРЅРѕ Р· РїРѕСЏСЃРЅРµРЅРЅСЏРј РґР»СЏ Р°РІС‚РѕСЂР°.",
      );
    } catch (error) {
      setModerationError(
        error instanceof Error ? error.message : "РќРµ РІРґР°Р»РѕСЃСЏ Р·Р°РІРµСЂС€РёС‚Рё РјРѕРґРµСЂР°С†С–СЋ.",
      );
    } finally {
      setModerationBusyId(null);
    }
  }

  return (
    <div className="workspace-grid">
      <section className="workspace-panel">
        <div className="workspace-panel__header">
          <span className="eyebrow">РџСѓР±Р»С–РєР°С†С–СЏ</span>
          <h3>{user ? `Р РѕР±РѕС‡Р° Р·РѕРЅР° ${user.full_name}` : "РџРѕРїРµСЂРµРґРЅС–Р№ РїРµСЂРµРіР»СЏРґ РєР°Р±С–РЅРµС‚Сѓ"}</h3>
        </div>
        <form className="stack-form" onSubmit={submitListing}>
          <label>
            РќР°Р·РІР° РѕРіРѕР»РѕС€РµРЅРЅСЏ
            <input
              value={listingForm.title}
              onChange={(event) =>
                setListingForm((current) => ({ ...current, title: event.target.value }))
              }
            />
          </label>
          <label>
            РћРїРёСЃ
            <textarea
              value={listingForm.description}
              onChange={(event) =>
                setListingForm((current) => ({ ...current, description: event.target.value }))
              }
            />
          </label>
          <div className="form-row">
            <label>
              Р¦С–РЅР°
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
              РљР°С‚РµРіРѕСЂС–СЏ
              <select
                value={listingForm.category_id}
                onChange={(event) =>
                  setListingForm((current) => ({ ...current, category_id: event.target.value }))
                }
              >
                <option value="">РћР±РµСЂС–С‚СЊ РєР°С‚РµРіРѕСЂС–СЋ</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label>
            РџРѕСЃРёР»Р°РЅРЅСЏ РЅР° Р·РѕР±СЂР°Р¶РµРЅРЅСЏ
            <textarea
              value={listingForm.image_urls}
              placeholder="РќРµРѕР±РѕРІ'СЏР·РєРѕРІРѕ. Р’РєР°Р¶С–С‚СЊ РїРѕРІРЅС– http/https URL, РїРѕ РѕРґРЅРѕРјСѓ РІ СЂСЏРґРєСѓ."
              onChange={(event) =>
                setListingForm((current) => ({ ...current, image_urls: event.target.value }))
              }
            />
          </label>
          <button className="cta-button" disabled={listingBusy} type="submit">
            {listingBusy ? "РџСѓР±Р»С–РєСѓС”РјРѕ..." : "РћРїСѓР±Р»С–РєСѓРІР°С‚Рё РѕРіРѕР»РѕС€РµРЅРЅСЏ"}
          </button>
          {listingError ? <p className="form-error">{listingError}</p> : null}
          {listingSuccess ? <p className="form-success">{listingSuccess}</p> : null}
        </form>
      </section>

      {canOperate ? (
        <section className="workspace-panel subtle">
          <div className="workspace-panel__header">
            <span className="eyebrow">РћРїРµСЂР°С†С–Р№РЅР° РїР°РЅРµР»СЊ</span>
            <h3>РњРѕРґРµСЂР°С†С–СЏ, РєР°С‚РµРіРѕСЂС–С— С‚Р° РїРѕРІС–РґРѕРјР»РµРЅРЅСЏ</h3>
          </div>
          <div className="mini-stats">
            <div>
              <strong>{pendingListings.length}</strong>
              <span>Р§РµРєР°СЋС‚СЊ РјРѕРґРµСЂР°С†С–С—</span>
            </div>
            <div>
              <strong>{messages.length}</strong>
              <span>РџРѕРІС–РґРѕРјР»РµРЅРЅСЏ</span>
            </div>
            <div>
              <strong>{myListings.length}</strong>
              <span>РњРѕС— РѕРіРѕР»РѕС€РµРЅРЅСЏ</span>
            </div>
          </div>
          <form className="stack-form compact" onSubmit={submitCategory}>
            <label>
              РќРѕРІР° РєР°С‚РµРіРѕСЂС–СЏ
              <input
                value={categoryForm.name}
                onChange={(event) =>
                  setCategoryForm((current) => ({ ...current, name: event.target.value }))
                }
              />
            </label>
            <label>
              РћРїРёСЃ РєР°С‚РµРіРѕСЂС–С—
              <input
                value={categoryForm.description}
                onChange={(event) =>
                  setCategoryForm((current) => ({ ...current, description: event.target.value }))
                }
              />
            </label>
            <button className="ghost-button" disabled={categoryBusy} type="submit">
              {categoryBusy ? "РЎС‚РІРѕСЂСЋС”РјРѕ..." : "Р”РѕРґР°С‚Рё РєР°С‚РµРіРѕСЂС–СЋ"}
            </button>
            {categoryError ? <p className="form-error">{categoryError}</p> : null}
            {categorySuccess ? <p className="form-success">{categorySuccess}</p> : null}
          </form>

          <section className="moderation-board">
            <div className="moderation-board__header">
              <div>
                <strong>Р§РµСЂРіР° РјРѕРґРµСЂР°С†С–С—</strong>
                <p>
                  РЁРІРёРґРєРѕ РїРµСЂРµРіР»СЏРґР°Р№С‚Рµ pending-РѕРіРѕР»РѕС€РµРЅРЅСЏ, СЃС…РІР°Р»СЋР№С‚Рµ СЏРєС–СЃРЅС– РїСѓР±Р»С–РєР°С†С–С— Р°Р±Рѕ
                  РїРѕРІРµСЂС‚Р°Р№С‚Рµ С—С… Р°РІС‚РѕСЂСѓ Р· РїРѕСЏСЃРЅРµРЅРЅСЏРј.
                </p>
              </div>
              <span className="status-pill">{pendingListings.length} Сѓ С‡РµСЂР·С–</span>
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
                      <span>{categoryMap.get(listing.category_id)?.name ?? "Р‘РµР· РєР°С‚РµРіРѕСЂС–С—"}</span>
                      <strong>${listing.price.toFixed(2)}</strong>
                    </div>

                    <p className="moderation-card__description">{listing.description}</p>

                    <label className="moderation-card__label">
                      РџСЂРёС‡РёРЅР° РІС–РґС…РёР»РµРЅРЅСЏ
                      <textarea
                        value={moderationNotes[listing.id] ?? ""}
                        placeholder="РќР°РїСЂРёРєР»Р°Рґ: РїРѕС‚СЂС–Р±РЅС– С‡С–С‚РєС–С€С– С„РѕС‚Рѕ, СѓС‚РѕС‡РЅС–С‚СЊ СЃС‚Р°РЅ С‚РѕРІР°СЂСѓ Р°Р±Рѕ Р·Р°РїРѕРІРЅС–С‚СЊ РѕРїРёСЃ."
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
                        {moderationBusyId === listing.id ? "РћР±СЂРѕР±Р»СЏС”РјРѕ..." : "РЎС…РІР°Р»РёС‚Рё"}
                      </button>
                      <button
                        className="cta-button moderation-card__reject"
                        disabled={moderationBusyId === listing.id}
                        type="button"
                        onClick={() => void moderateListing(listing.id, false)}
                      >
                        {moderationBusyId === listing.id ? "РћР±СЂРѕР±Р»СЏС”РјРѕ..." : "Р’С–РґС…РёР»РёС‚Рё"}
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-card moderation-empty">
                  <strong>Р§РµСЂРіР° С‡РёСЃС‚Р°</strong>
                  <p>РќР°СЂР°Р·С– РЅРµРјР°С” pending-РѕРіРѕР»РѕС€РµРЅСЊ. РќРѕРІС– РїСѓР±Р»С–РєР°С†С–С— Р·'СЏРІР»СЏСЋС‚СЊСЃСЏ С‚СѓС‚ Р°РІС‚РѕРјР°С‚РёС‡РЅРѕ.</p>
                </div>
              )}
            </div>
          </section>

          <div className="workspace-list-preview">
            <div>
              <strong>РћСЃС‚Р°РЅРЅС– РїРѕРІС–РґРѕРјР»РµРЅРЅСЏ</strong>
              <ul>
                {messages.length ? (
                  messages.slice(0, 3).map((message) => <li key={message.id}>{message.body}</li>)
                ) : (
                  <li>РџРѕРєРё С‰Рѕ РїРѕРІС–РґРѕРјР»РµРЅСЊ РЅРµРјР°С”.</li>
                )}
              </ul>
            </div>
            <div>
              <strong>Р©Рѕ РїРµСЂРµРІС–СЂСЏС‚Рё РЅР°СЃР°РјРїРµСЂРµРґ</strong>
              <ul>
                <li>Р§Рё РґРѕСЃС‚Р°С‚РЅСЊРѕ РєРѕРЅРєСЂРµС‚РЅРёР№ Р·Р°РіРѕР»РѕРІРѕРє.</li>
                <li>Р§Рё РѕРїРёСЃ РґР°С” РїРѕРєСѓРїС†СЋ РїРѕРІРЅСѓ РєР°СЂС‚РёРЅСѓ.</li>
                <li>Р§Рё С” Р°РґРµРєРІР°С‚РЅР° С†С–РЅР° С‚Р° РєРѕСЂРµРєС‚РЅР° РєР°С‚РµРіРѕСЂС–СЏ.</li>
              </ul>
            </div>
          </div>
        </section>
      ) : null}

      <section className="workspace-panel wide">
        <div className="workspace-panel__header">
          <span className="eyebrow">РђСЃРѕСЂС‚РёРјРµРЅС‚</span>
          <h3>Р’Р°С€С– РїРѕС‚РѕС‡РЅС– РѕРіРѕР»РѕС€РµРЅРЅСЏ</h3>
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
              <strong>РџРѕРєРё С‰Рѕ РЅРµРјР°С” Р¶РѕРґРЅРѕРіРѕ РѕРіРѕР»РѕС€РµРЅРЅСЏ</strong>
              <p>РЎС‚РІРѕСЂС–С‚СЊ РїРµСЂС€Сѓ РїСѓР±Р»С–РєР°С†С–СЋ Сѓ РІРµСЂС…РЅС–Р№ С„РѕСЂРјС–, С– РІРѕРЅР° РѕРґСЂР°Р·Сѓ Р·'СЏРІРёС‚СЊСЃСЏ С‚СѓС‚.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
