import { Play } from "lucide-react";
import { useState } from "react";
import type { ModuleData, VideoMaterial } from "../types";
import { VideoPlayer } from "./VideoPlayer";

function formatVideoCount(count: number) {
  const lastTwoDigits = count % 100;
  const lastDigit = count % 10;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) return `${count} учебных роликов`;
  if (lastDigit === 1) return `${count} учебный ролик`;
  if (lastDigit >= 2 && lastDigit <= 4) return `${count} учебных ролика`;
  return `${count} учебных роликов`;
}

export function VideoMaterials({ module }: { module: ModuleData }) {
  const [activeVideo, setActiveVideo] = useState<VideoMaterial | null>(null);

  return (
    <>
      <section className="materials-panel">
        <div className="materials-heading">
          <div><span>ВИДЕОМАТЕРИАЛЫ</span><h2>Практика работы с {module.shortName}</h2></div>
          <p>{formatVideoCount(module.videos.length)}</p>
        </div>
        <div className="video-grid">
          {module.videos.map((item, index) => (
            <button
              className={`video-card ${item.file ? "" : "is-unavailable"}`}
              key={item.title}
              type="button"
              onClick={() => item.file && setActiveVideo(item)}
              disabled={!item.file}
              aria-label={item.file ? `Открыть видео: ${item.title}` : `Видео пока не загружено: ${item.title}`}
            >
              <div
                className="video-preview"
                style={{ backgroundImage: `url(${module.cover})` }}
              >
                <span className="video-index">{String(index + 1).padStart(2, "0")}</span>
                <span className="play-button"><Play size={20} fill="currentColor" /></span>
                <span className="duration">{item.file ? item.duration : "НЕТ ФАЙЛА"}</span>
              </div>
              <div className="video-copy"><h3>{item.title}</h3><p>{item.description}</p></div>
            </button>
          ))}
        </div>
      </section>
      {activeVideo && <VideoPlayer material={activeVideo} poster={module.cover} onClose={() => setActiveVideo(null)} />}
    </>
  );
}
