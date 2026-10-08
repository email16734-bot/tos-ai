"use client";

import { useEffect, useState } from "react";
import { AppMark } from "./components/AppMark";
import { Catalog } from "./components/Catalog";
import { Module } from "./components/Module";
import { ShellHeader } from "./components/ShellHeader";
import type { ModuleData, Theme } from "./types";

export default function TrainingApp() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [modules, setModules] = useState<ModuleData[]>([]);
  const [loadError, setLoadError] = useState(false);
  const [selected, setSelected] = useState<ModuleData | null>(null);

  useEffect(() => {
    const saved = window.localStorage.getItem("training-theme") as Theme | null;
    if (saved !== "dark" && saved !== "light") return;

    const timer = window.setTimeout(() => setTheme(saved), 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const loadModules = async () => {
      try {
        const indexResponse = await fetch("/training-content/index.json");
        if (!indexResponse.ok) throw new Error("Не удалось загрузить индекс модулей");

        const moduleIds = (await indexResponse.json()) as string[];
        const loaded = await Promise.all(
          moduleIds.map(async (moduleId) => {
            const response = await fetch(`/training-content/${moduleId}/module.json`);
            if (!response.ok) throw new Error(`Не удалось загрузить модуль ${moduleId}`);
            return (await response.json()) as ModuleData;
          }),
        );

        if (!cancelled) {
          setModules(loaded);
          setLoadError(false);
        }
      } catch {
        if (!cancelled) setLoadError(true);
      }
    };

    void loadModules();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (modules.length === 0) return;

    const syncFromUrl = () => {
      const moduleId = new URLSearchParams(window.location.search).get("module");
      setSelected(modules.find((item) => item.id === moduleId) ?? null);
    };

    syncFromUrl();
    window.addEventListener("popstate", syncFromUrl);
    return () => window.removeEventListener("popstate", syncFromUrl);
  }, [modules]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("training-theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme((value) => (value === "dark" ? "light" : "dark"));

  const openModule = (module: ModuleData) => {
    window.history.pushState({}, "", `?module=${module.id}`);
    setSelected(module);
    window.scrollTo(0, 0);
  };

  const closeModule = () => {
    window.history.pushState({}, "", window.location.pathname);
    setSelected(null);
    window.scrollTo(0, 0);
  };

  if (modules.length === 0) {
    return (
      <main className="catalog-page loading-page">
        <ShellHeader theme={theme} onToggleTheme={toggleTheme} />
        <div className="module-loading">
          <AppMark />
          <span>{loadError ? "Не удалось загрузить модули" : "Подготовка учебной среды"}</span>
          {!loadError && <i />}
        </div>
      </main>
    );
  }

  return selected ? (
    <Module module={selected} theme={theme} onToggleTheme={toggleTheme} onBack={closeModule} />
  ) : (
    <Catalog modules={modules} theme={theme} onToggleTheme={toggleTheme} onOpen={openModule} />
  );
}
