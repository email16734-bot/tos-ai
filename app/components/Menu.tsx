import { BookOpen, Box, Video } from "lucide-react";
import type { ModuleData, ModuleTab } from "../types";

type MenuProps = {
  activeTab: ModuleTab;
  module: ModuleData;
  onChange: (tab: ModuleTab) => void;
  menuVisible: boolean;
};

export function Menu({ activeTab, module, onChange, menuVisible }: MenuProps) {
  return (
    <nav className="module-dock" aria-label="Материалы модуля" style={{display: menuVisible ? "flex" : "none"}}>
      <button className={activeTab === "model" ? "is-active" : ""} onClick={() => onChange("model")}>
        <Box size={20} /><span>3D</span><small>Модель</small>
      </button>
      <span className="dock-divider" />
      <button className={activeTab === "video" ? "is-active" : ""} onClick={() => onChange("video")}>
        <Video size={20} /><span>Видео</span><small>Материалов: {module.videos.length}</small>
      </button>
      <span className="dock-divider" />
      <button className={activeTab === "text" ? "is-active" : ""} onClick={() => onChange("text")}>
        <BookOpen size={20} /><span>Тексты</span><small>Документов: {module.texts.length}</small>
      </button>
    </nav>
  );
}
