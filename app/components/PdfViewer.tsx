import { Download, Minus, Plus, X } from "lucide-react";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";
import { useEffect, useRef, useState } from "react";
import type { TextMaterial } from "../types";

type PdfViewerProps = {
  material: TextMaterial;
  onClose: () => void;
};

type PdfPageProps = {
  document: PDFDocumentProxy;
  pageNumber: number;
  zoom: number;
};

function PdfPage({ document, pageNumber, zoom }: PdfPageProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    let renderTask: ReturnType<PDFPageProxy["render"]> | null = null;

    const renderPage = async () => {
      const host = hostRef.current;
      const canvas = canvasRef.current;
      if (!host || !canvas) return;

      const page = await document.getPage(pageNumber);
      if (cancelled) return;

      const baseViewport = page.getViewport({ scale: 1 });
      const availableWidth = Math.max(280, Math.min(980, host.clientWidth));
      const fitScale = availableWidth / baseViewport.width;
      const viewport = page.getViewport({ scale: fitScale * zoom });
      const outputScale = Math.min(window.devicePixelRatio || 1, 2);
      const context = canvas.getContext("2d", { alpha: false });
      if (!context) return;

      canvas.width = Math.floor(viewport.width * outputScale);
      canvas.height = Math.floor(viewport.height * outputScale);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;

      renderTask = page.render({
        canvas,
        canvasContext: context,
        viewport,
        transform: outputScale === 1 ? undefined : [outputScale, 0, 0, outputScale, 0, 0],
      });
      await renderTask.promise;
    };

    void renderPage();
    return () => {
      cancelled = true;
      renderTask?.cancel();
    };
  }, [document, pageNumber, zoom]);

  return (
    <article className="pdf-page" ref={hostRef} aria-label={`Страница ${pageNumber}`}>
      <canvas ref={canvasRef} />
      <span>{pageNumber}</span>
    </article>
  );
}

export function PdfViewer({ material, onClose }: PdfViewerProps) {
  const [document, setDocument] = useState<PDFDocumentProxy | null>(null);
  const [error, setError] = useState(false);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    let cancelled = false;
    let loadingTask: { destroy: () => Promise<void> } | null = null;

    const loadDocument = async () => {
      try {
        const pdfjs = await import("pdfjs-dist");
        pdfjs.GlobalWorkerOptions.workerSrc = new URL(
          "pdfjs-dist/build/pdf.worker.min.mjs",
          import.meta.url,
        ).toString();
        const task = pdfjs.getDocument({ url: material.file });
        loadingTask = task;
        const loadedDocument = await task.promise;
        if (!cancelled) setDocument(loadedDocument);
      } catch (loadError) {
        console.error("Не удалось загрузить PDF", loadError);
        if (!cancelled) setError(true);
      }
    };

    void loadDocument();
    return () => {
      cancelled = true;
      void loadingTask?.destroy();
    };
  }, [material.file]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div className="pdf-viewer-overlay" role="dialog" aria-modal="true" aria-label={material.title}>
      <header className="pdf-viewer-header">
        <div className="pdf-title">
          <span>PDF-ДОКУМЕНТ</span>
          <strong>{material.title}</strong>
        </div>
        <div className="pdf-header-actions">
          <div className="pdf-zoom" aria-label="Масштаб документа">
            <button onClick={() => setZoom((value) => Math.max(0.7, value - 0.1))} aria-label="Уменьшить масштаб"><Minus size={16} /></button>
            <span>{Math.round(zoom * 100)}%</span>
            <button onClick={() => setZoom((value) => Math.min(1.5, value + 0.1))} aria-label="Увеличить масштаб"><Plus size={16} /></button>
          </div>
          <a href={material.file} download><Download size={17} /><span>Скачать</span></a>
          <button onClick={onClose} aria-label="Закрыть документ"><X size={20} /></button>
        </div>
      </header>

      <div className="pdf-scroll">
        {!document && !error && (
          <div className="pdf-status"><i /><span>Загрузка документа</span></div>
        )}
        {error && (
          <div className="pdf-status pdf-error">
            <strong>Не удалось открыть документ</strong>
            <a href={material.file} target="_blank" rel="noreferrer">Открыть PDF в браузере</a>
          </div>
        )}
        {document && (
          <div className="pdf-pages">
            {Array.from({ length: document.numPages }, (_, index) => (
              <PdfPage key={index + 1} document={document} pageNumber={index + 1} zoom={zoom} />
            ))}
          </div>
        )}
      </div>

      <footer className="pdf-viewer-footer">
        <span>{document ? `${document.numPages} стр.` : "PDF"}</span>
        <span>Прокрутите документ для чтения</span>
      </footer>
    </div>
  );
}