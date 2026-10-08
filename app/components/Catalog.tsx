import { Radio, Search, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { ModuleData, Theme } from "../types";
import { ModuleCard } from "./ModuleCard";
import { ShellHeader } from "./ShellHeader";

type CatalogProps = {
  modules: ModuleData[];
  theme: Theme;
  onToggleTheme: () => void;
  onOpen: (module: ModuleData) => void;
};

export function Catalog({ modules, theme, onToggleTheme, onOpen }: CatalogProps) {
  const [activeTab, setActiveTab] = useState("all");
  const tabs = [
    {id: "all", title: "Все"},
    {id: "radiostations", title: "Носимые радиостанции"},
    {id: "autos", title: "Автомобильная техника"},
    {id: "sputniks", title: "Спутниковая связь"}
  ]
  const [query, setQuery] = useState("");
  const visibleModules = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return modules;

    return modules.filter((item) =>
      [item.name, item.category, item.description].some((value) =>
        value.toLowerCase().includes(normalized),
      ),
    );
  }, [modules, query]);

  return (
    <main className="catalog-page">
      <ShellHeader theme={theme} onToggleTheme={onToggleTheme} />

      <section className="catalog-hero">
        <div className="eyebrow"><Radio size={14} /> СРЕДСТВА ВОЕННОЙ СВЯЗИ</div>
        <h1>Обучающий модуль<br></br>тренажерно-обучающей системы</h1>
        <p>
          Изучайте устройство техники в интерактивном формате: исследуйте 3D-модели,
          разбирайте ключевые узлы и переходите к учебным материалам.
        </p>
        {/*<div className="hero-facts" aria-label="Сводка каталога">
          <div><strong>{modules.length}</strong><span>учебных модуля</span></div>
          <div><strong>3</strong><span>формата обучения</span></div>
        </div>*/}
      </section>

      <section className="catalog-content">
        <div className="section-heading">
          <div>
            <span className="section-index">01</span>
            <div>
              <h2>Выберите технику</h2>
              <p>Откройте модуль, чтобы начать изучение</p>
            </div>
          </div>
          <label className="search-field">
            <Search size={17} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Найти технику"
              aria-label="Найти технику"
            />
            {query && (
              <button onClick={() => setQuery("")} aria-label="Очистить поиск"><X size={15} /></button>
            )}
          </label>
        </div>
        <div className="catalog-tabs">
                  {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    className={`catalog-tab ${activeTab === tab.id ? "active" : ""}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.title}
                  </button>
        ))}
          </div>
        <div>
          {activeTab === "all" && (
            <div className="module-grid">
              {visibleModules
              .map((module) => (
                <ModuleCard key={module.id} module={module} onOpen={onOpen} />
              ))}
            </div>           
          )}
          {activeTab === "radiostations" && (
            <div className="module-grid">
              {visibleModules
              .filter((module) => module.category === "radiostations")
              .map((module) => (
                <ModuleCard key={module.id} module={module} onOpen={onOpen} />
              ))}
            </div>           
          )}
            {activeTab === "autos" && (
            <div className="module-grid">
              {visibleModules
              .filter((module) => module.category === "autos")
              .map((module) => (
                <ModuleCard key={module.id} module={module} onOpen={onOpen} />
              ))}
            </div>           
          )}
            {activeTab === "sputniks" && (
            <div className="module-grid">
              {visibleModules
              .filter((module) => module.category === "sputniks")
              .map((module) => (
                <ModuleCard key={module.id} module={module} onOpen={onOpen} />
              ))}
            </div>           
          )}
        </div>
        {visibleModules.length === 0 && (
          <div className="empty-state">
            <Search size={24} />
            <h3>Ничего не найдено</h3>
            <p>Попробуйте изменить поисковый запрос.</p>
          </div>
        )}
      </section>

      <footer className="catalog-footer">
        <span>Военная академия связи • 2026</span>
        <span>v.0.1</span>
      </footer>
    </main>
  );
}
