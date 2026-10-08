import { ChevronRight, Clock3, FileText } from "lucide-react";
import { useState } from "react";
import type { ModuleData, TextMaterial } from "../types";
import { PdfViewer } from "./PdfViewer";

export function TextMaterials({ module }: { module: ModuleData }) {
  const [activeDocument, setActiveDocument] = useState<TextMaterial | null>(null);

  return (
    <>
      <section className="materials-panel text-panel">
        <div className="materials-heading">
          <div><span>PDF-МАТЕРИАЛЫ</span><h2>Учебная документация</h2><h3>{module.sklon}</h3></div>
          <p>Вся техническая документация не распространяется через открытые источники<br></br>и хранится исключительно в папке обучающего модуля</p> 
        </div>
        <div className="document-list">
          {module.texts.map((item) => (
            <button className="document-card pdf-document-card" key={item.title} onClick={() => setActiveDocument(item)}>
              <span className="document-icon"><FileText size={21} /></span>
              <span className="document-main">
                <span className="document-meta">{item.type} <i /> <Clock3 size={13} /> {item.readTime}</span>
                <strong>{item.title}</strong>
                <span className="document-description">{item.description}</span>
                <span className="open-book-label">Открыть PDF <ChevronRight size={15} /></span>
              </span>
              <span className="pdf-badge">PDF</span>
            </button>
          ))}
        </div>
      </section>
      {activeDocument && <PdfViewer material={activeDocument} onClose={() => setActiveDocument(null)} />}
    </>
  );
}