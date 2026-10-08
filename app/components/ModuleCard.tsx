import { Box, ChevronRight } from "lucide-react";
import type { ModuleData } from "../types";

type ModuleCardProps = {
  module: ModuleData;
  onOpen: (module: ModuleData) => void;
};

export function ModuleCard({ module, onOpen }: ModuleCardProps) {
  return (
    <button
      className={`module-card`}
      onClick={() => onOpen(module)}
    >
      <div
        className="module-cover"
        style={{
          backgroundImage: `url(${module.cover})`,
        }}
      >
        <span className="module-mode"><Box size={14} /> 3D</span>
        {/*<span className="module-glow" />*/}
      </div>
      <div className="module-card-body">
        <div className="module-category">{module.subcategory}</div>
        <h3>{module.name}</h3>
        <p>{module.description}</p>
        <div className="module-card-footer">
          <span className="open-module">Открыть <ChevronRight size={17} /></span>
        </div>
      </div>
    </button>
  );
}