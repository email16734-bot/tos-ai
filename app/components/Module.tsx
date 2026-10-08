import { ArrowLeft, Eye, EyeOff, RotateCcw } from "lucide-react";
import { useState } from "react";
import type { ModuleData, ModuleTab, Theme } from "../types";
import { AppMark } from "./AppMark";
import { Menu } from "./Menu";
import { ModelOverview } from "./ModelOverview";
import { TextMaterials } from "./TextMaterials";
import { ThemeButton } from "./ThemeButton";
import { VideoMaterials } from "./VideoMaterials";

type ModuleProps = {
  module: ModuleData;
  theme: Theme;
  onToggleTheme: () => void;
  onBack: () => void;
};

export function Module({ module, theme, onToggleTheme, onBack }: ModuleProps) {
  const [activeTab, setActiveTab] = useState<ModuleTab>("model");
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null);
  const [hotspotsVisible, setHotspotsVisible] = useState(true);
  const [resetToken, setResetToken] = useState(0);
  const [menuVisible, setMenuVisible] = useState(true);

  const resetView = () => {
    setActiveHotspot(null);
    setResetToken((value) => value + 1);
  };

  const toggleHotspots = () => {
    setHotspotsVisible((visible) => !visible);
    setActiveHotspot(null);
  };

  return (
    <main className="module-page">
      <header className="module-header">
        <div className="module-header-left">
          <button className="back-button" onClick={onBack}>
            <ArrowLeft size={18} /> Каталог
          </button>
          <span className="header-divider" />
          <AppMark />
          <div className="module-title">
            <span>{module.subcategory}</span>
            <strong>{module.name}</strong>
          </div>
        </div>
        <div className="module-progress">
          <span className="system-status">
            <i /> Военная академия связи
          </span>
          <ThemeButton theme={theme} onToggle={onToggleTheme} />
        </div>
      </header>

      <div className="module-workspace">
        {activeTab === "model" && (
          <ModelOverview
            module={module}
            activeHotspot={activeHotspot}
            onHotspot={setActiveHotspot}
            hotspotsVisible={hotspotsVisible}
            resetToken={resetToken}
            onPanoramaChange={setMenuVisible}
          />
        )}
        {activeTab === "video" && <VideoMaterials module={module} />}
        {activeTab === "text" && <TextMaterials module={module} />}
      </div>

      {activeTab === "model" && (
        <div className="model-actions">
          <button
            className="model-action"
            onClick={resetView}
            aria-label="Сбросить положение"
          >
            <RotateCcw size={17} />
          </button>
          <button
            className={`model-action hotspot-toggle ${hotspotsVisible ? "is-active" : ""}`}
            onClick={toggleHotspots}
            aria-label={hotspotsVisible ? "Скрыть точки" : "Показать точки"}
            aria-pressed={hotspotsVisible}
          >
            {hotspotsVisible ? <Eye size={17} /> : <EyeOff size={17} />}
          </button>
        </div>
      )}

      <Menu
        activeTab={activeTab}
        module={module}
        onChange={setActiveTab}
        menuVisible={menuVisible}
      />
    </main>
  );
}
