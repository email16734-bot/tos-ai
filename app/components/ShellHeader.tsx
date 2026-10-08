import type { Theme } from "../types";
import { AppMark } from "./AppMark";
import { ThemeButton } from "./ThemeButton";

type ShellHeaderProps = {
  theme: Theme;
  onToggleTheme: () => void;
};

export function ShellHeader({ theme, onToggleTheme }: ShellHeaderProps) {
  return (
    <header className="shell-header">
      <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
        <AppMark />
        <span className="brand-copy">
          <strong>ТРЕНАЖЕРНО-ОБУЧАЮЩАЯ СИСТЕМА</strong>
          <small>тренажерная среда</small>
        </span>
      </button>
      <div className="header-meta">
        <span className="system-status"><i /> Военная академия связи</span>
        <ThemeButton theme={theme} onToggle={onToggleTheme} />
      </div>
    </header>
  );
}