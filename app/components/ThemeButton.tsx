import { Moon, Sun } from "lucide-react";
import type { Theme } from "../types";

type ThemeButtonProps = {
  theme: Theme;
  onToggle: () => void;
};

export function ThemeButton({ theme, onToggle }: ThemeButtonProps) {
  return (
    <button className="icon-button theme-button" onClick={onToggle} aria-label="Сменить тему">
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
