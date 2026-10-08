import { Download, Film, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { VideoMaterial } from "../types";

type VideoPlayerProps = {
  material: VideoMaterial;
  poster: string;
  onClose: () => void;
};

export function VideoPlayer({ material, poster, onClose }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  useEffect(() => {
    const video = videoRef.current;
    return () => {
      video?.pause();
    };
  }, []);

  return (
    <div className="video-player-overlay" role="dialog" aria-modal="true" aria-label={material.title}>
      <header className="video-player-header">
        <div className="video-player-title">
          <span>ВИДЕОМАТЕРИАЛ</span>
          <strong>{material.title}</strong>
        </div>
        <div className="video-player-actions">
          {/*{material.file && (
            <a href={material.file} download>
              <Download size={17} />
              <span>Скачать</span>
            </a>
          )}*/}
          <button type="button" onClick={onClose} aria-label="Закрыть видео">
            <X size={20} />
          </button>
        </div>
      </header>

      <div className="video-player-stage">
        {!isReady && !hasError && (
          <div className="video-player-status" role="status">
            <i />
            <span>Загрузка видеоматериала</span>
          </div>
        )}

        {hasError && (
          <div className="video-player-status video-player-error">
            <Film size={34} />
            <strong>Не удалось воспроизвести видео</strong>
            {material.file && <a href={material.file} target="_blank" rel="noreferrer">Открыть файл в браузере</a>}
          </div>
        )}

        {material.file && (
          <video
            ref={videoRef}
            className={isReady ? "is-ready" : ""}
            src={material.file}
            poster={poster}
            controls
            autoPlay
            playsInline
            preload="metadata"
            onCanPlay={() => setIsReady(true)}
            onError={() => setHasError(true)}
          >
            Ваш браузер не поддерживает воспроизведение видео.
          </video>
        )}
      </div>

      <footer className="video-player-footer">
        <span>{material.duration}</span>
        <span>{material.description}</span>
      </footer>
    </div>
  );
}
