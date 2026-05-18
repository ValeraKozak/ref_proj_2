import { useEffect, useState } from "react";

import { ListingCard } from "../components/ListingCard";
import { SectionTitle } from "../components/SectionTitle";
import { api } from "../lib/api";
import type { Category, Listing, ListingFilters } from "../lib/types";

interface CatalogPageProps {
  categories: Category[];
}

const DEFAULT_FILTERS: Required<Pick<ListingFilters, "sort_by" | "sort_order">> = {
  sort_by: "created_at",
  sort_order: "desc",
};

export function CatalogPage({ categories }: Readonly<CatalogPageProps>) {
  const [filters, setFilters] = useState({
    query: "",
    category_id: "",
    min_price: "",
    max_price: "",
    sort_by: DEFAULT_FILTERS.sort_by,
    sort_order: DEFAULT_FILTERS.sort_order,
  });
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = globalThis.setTimeout(() => {
      setIsLoading(true);
      setError("");
      api
        .listings({
          query: filters.query || undefined,
          category_id: filters.category_id ? Number(filters.category_id) : undefined,
          min_price: filters.min_price ? Number(filters.min_price) : undefined,
          max_price: filters.max_price ? Number(filters.max_price) : undefined,
          sort_by: filters.sort_by,
          sort_order: filters.sort_order,
        })
        .then((result) => {
          if (!controller.signal.aborted) {
            setListings(result);
          }
        })
        .catch((loadError) => {
          if (!controller.signal.aborted) {
            setError(loadError instanceof Error ? loadError.message : "Failed to load listings.");
            setListings([]);
          }
        })
        .finally(() => {
          if (!controller.signal.aborted) {
            setIsLoading(false);
          }
        });
    }, 180);

    return () => {
      controller.abort();
      globalThis.clearTimeout(timeoutId);
    };
  }, [filters]);

  return (
    <div className="page-shell">
      <section className="content-block split-layout">
        <div className="catalog-sidebar">
          <SectionTitle
            eyebrow="Пошук без тертя"
            title="Фільтруйте як покупець, а не як тестувальник API"
            body="Введіть запит, оберіть категорію й одразу отримайте зрозумілу вітрину. Логіка працює через backend, але для користувача відчувається легкою."
          />
          <form className="stack-form catalog-filter-panel">
            <label>
              <span>Що ви шукаєте</span>
              <input
                placeholder="ноутбук, велосипед, послуги..."
                value={filters.query}
                onChange={(event) =>
                  setFilters((current) => ({ ...current, query: event.target.value }))
                }
              />
            </label>
            <label>
              <span>Категорія</span>
              <select
                value={filters.category_id}
                onChange={(event) =>
                  setFilters((current) => ({ ...current, category_id: event.target.value }))
                }
              >
                <option value="">Усі категорії</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
            <div className="form-row">
              <label>
                <span>Ціна від</span>
                <input
                  type="number"
                  min="0"
                  value={filters.min_price}
                  onChange={(event) =>
                    setFilters((current) => ({ ...current, min_price: event.target.value }))
                  }
                />
              </label>
              <label>
                <span>Ціна до</span>
                <input
                  type="number"
                  min="0"
                  value={filters.max_price}
                  onChange={(event) =>
                    setFilters((current) => ({ ...current, max_price: event.target.value }))
                  }
                />
              </label>
            </div>
            <div className="form-row">
              <label>
                <span>Сортувати за</span>
                <select
                  value={filters.sort_by}
                  onChange={(event) =>
                    setFilters((current) => ({
                      ...current,
                      sort_by: event.target.value as "created_at" | "price",
                    }))
                  }
                >
                  <option value="created_at">Новизною</option>
                  <option value="price">Ціною</option>
                </select>
              </label>
              <label>
                <span>Порядок</span>
                <select
                  value={filters.sort_order}
                  onChange={(event) =>
                    setFilters((current) => ({
                      ...current,
                      sort_order: event.target.value as "asc" | "desc",
                    }))
                  }
                >
                  <option value="desc">Спадання</option>
                  <option value="asc">Зростання</option>
                </select>
              </label>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={() =>
                setFilters({
                  query: "",
                  category_id: "",
                  min_price: "",
                  max_price: "",
                  sort_by: DEFAULT_FILTERS.sort_by,
                  sort_order: DEFAULT_FILTERS.sort_order,
                })
              }
            >
              Скинути фільтри
            </button>
          </form>
          <div className="category-column">
            {categories.length ? (
              categories.map((category) => (
                <div className="category-pill" key={category.id}>
                  <strong>{category.name}</strong>
                  <span>{category.description}</span>
                </div>
              ))
            ) : (
              <div className="empty-card">
                <strong>Категорій поки немає</strong>
                <p>Додайте їх із кабінету або через адміністративний API.</p>
              </div>
            )}
          </div>
        </div>
        <div className="catalog-main">
          <SectionTitle
            eyebrow="Вітрина"
            title="Підібрані результати без перевантаження інтерфейсу"
            body="Оголошення подаються великими картками, щоб користувачу було легко оцінити релевантність, фото і ціну ще до переходу в деталі."
          />
          {error ? <p className="form-error">{error}</p> : null}
          <div className="catalog-results-bar">
            <strong>{isLoading ? "Завантаження..." : `${listings.length} результатів`}</strong>
            <span>Запит, категорія, діапазон ціни і сортування працюють напряму через API.</span>
          </div>
          <div className="listing-grid">
            {listings.length ? (
              listings.map((listing) => (
                <ListingCard
                  key={listing.id}
                  listing={listing}
                  category={categories.find((category) => category.id === listing.category_id)}
                />
              ))
            ) : (
              <div className="empty-card">
                <strong>
                  {isLoading
                    ? "Оновлюємо вітрину"
                    : "За цим набором фільтрів нічого не знайдено"}
                </strong>
                <p>
                  {isLoading
                    ? "Каталог завантажує свіжі дані з сервера."
                    : "Спробуйте розширити ціновий діапазон, змінити запит або очистити категорію."}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
