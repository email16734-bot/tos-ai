import { Box, Move3d, X, ZoomIn, ZoomOut } from "lucide-react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import { useEffect, useRef, useState } from "react";
import type { Hotspot, ModuleData } from "../types";
import { Panorama } from "./Panorama";

type ModelOverviewProps = {
  module: ModuleData;
  activeHotspot: string | null;
  onHotspot: (id: string | null) => void;
  hotspotsVisible: boolean;
  resetToken: number;
  onPanoramaChange: (visible: boolean) => void;
};

type HotspotOverlayProps = {
  hotspots: Hotspot[];
  activeId: string | null;
  onSelect: (id: string | null) => void;
};

type ModelViewerInstance = HTMLElement & {
  cameraOrbit: string;
  cameraTarget: string;
  fieldOfView: string;
  interpolationDecay: number;
  loaded?: boolean;
  getCameraOrbit: () => { theta: number; phi: number; radius: number };
};

function HotspotOverlay({ hotspots, activeId, onSelect }: HotspotOverlayProps) {
  const active = hotspots.find((item) => item.id === activeId) ?? null;

  return (
    <div className="hotspot-layer">
      {hotspots.map((hotspot, index) => (
        <button
          key={hotspot.id}
          className={`hotspot-dot ${activeId === hotspot.id ? "is-active" : ""}`}
          style={
            {
              width: "48px",
              height: "48px",
              "--x": `${hotspot.screen.x}%`,
              "--y": `${hotspot.screen.y}%`,
            } as CSSProperties
          }
          onPointerDown={(event) => event.stopPropagation()}
          onClick={(event) => {
            event.stopPropagation();
            onSelect(activeId === hotspot.id ? null : hotspot.id);
          }}
          aria-label={`Открыть описание: ${hotspot.label}`}
        >
          <span>{String(index + 1).padStart(2, "0")}</span>
        </button>
      ))}

      {active && (
        <div
          className={`hotspot-annotation ${active.screen.x > 58 ? "align-left" : "align-right"}`}
          style={
            {
              "--x": `${active.screen.x}%`,
              "--y": `${active.screen.y}%`,
            } as CSSProperties
          }
        >
          <span className="annotation-line" />
          <div className="annotation-card">
            <div className="annotation-topline">
              <button
                onClick={() => onSelect(null)}
                aria-label="Закрыть описание"
              >
                <X size={15} />
              </button>
            </div>
            <h3>{active.label}</h3>
            <p>{active.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}

function PlaceholderViewer({
  module,
  activeHotspot,
  onHotspot,
  hotspotsVisible,
}: ModelOverviewProps) {
  const [rotation, setRotation] = useState({ x: -7, y: -12 });
  const [scale, setScale] = useState(1);
  const drag = useRef({ active: false, x: 0, y: 0 });

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    drag.current = { active: true, x: event.clientX, y: event.clientY };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!drag.current.active) return;

    const deltaX = event.clientX - drag.current.x;
    const deltaY = event.clientY - drag.current.y;
    drag.current = { active: true, x: event.clientX, y: event.clientY };
    setRotation((value) => ({
      x: Math.max(-45, Math.min(45, value.x - deltaY * 0.16)),
      y: value.y + deltaX * 0.22,
    }));
  };

  return (
    <div
      className="model-stage"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={() => {
        drag.current.active = false;
      }}
      onPointerCancel={() => {
        drag.current.active = false;
      }}
      onWheel={(event) => {
        event.preventDefault();
        setScale((value) =>
          Math.max(0.72, Math.min(1.35, value - event.deltaY * 0.0008)),
        );
      }}
      onClick={() => onHotspot(null)}
    >
      <div className="stage-grid" />
      <div className="stage-orbit orbit-one" />
      <div className="stage-orbit orbit-two" />
      <div className="model-shadow" />
      <div
        className={`placeholder-object`}
        style={{
          transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(${scale})`,
        }}
      >
        <div
          className="placeholder-image"
          style={{
            backgroundImage: `url(${module.cover})`,
          }}
        />
        <span className="placeholder-depth depth-one" />
        <span className="placeholder-depth depth-two" />
      </div>

      {hotspotsVisible && (
        <HotspotOverlay
          hotspots={module.hotspots}
          activeId={activeHotspot}
          onSelect={onHotspot}
        />
      )}

      <div className="model-placeholder-label">
        <Box size={15} />
        <span>
          <strong>MODEL.GLB</strong> место для модели
        </span>
      </div>

      <div className="viewer-help">
        <Move3d size={16} />
        <span>Зажмите и перемещайте для вращения</span>
      </div>

      <div className="zoom-controls">
        <button
          onPointerDown={(event) => event.stopPropagation()}
          onClick={(event) => {
            event.stopPropagation();
            setScale((value) => Math.min(1.35, value + 0.1));
          }}
          aria-label="Приблизить"
        >
          <ZoomIn size={18} />
        </button>
        <span />
        <button
          onPointerDown={(event) => event.stopPropagation()}
          onClick={(event) => {
            event.stopPropagation();
            setScale((value) => Math.max(0.72, value - 0.1));
          }}
          aria-label="Отдалить"
        >
          <ZoomOut size={18} />
        </button>
      </div>
    </div>
  );
}

function GlbViewer({
  module,
  activeHotspot,
  onHotspot,
  hotspotsVisible,
  resetToken,
  onPanoramaChange,
}: ModelOverviewProps) {
  const viewer = useRef<HTMLElement | null>(null);
  const focusTimer = useRef<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const ModelViewerElement = "model-viewer" as React.ElementType;
  const [panoramaVisible, setPanoramaVisible] = useState(false);

  const showPanorama = () => {
    setPanoramaVisible((visible) => !visible);
    onPanoramaChange(false);
  };

  useEffect(() => {
    void import("@google/model-viewer");
  }, []);

  useEffect(() => {
    const element = viewer.current as ModelViewerInstance | null;
    if (!element) return;

    const handleLoad = () => setIsLoading(false);
    element.addEventListener("load", handleLoad);
    if (element.loaded) handleLoad();

    return () => element.removeEventListener("load", handleLoad);
  }, [module.id]);

  useEffect(() => {
    const element = viewer.current as ModelViewerInstance | null;
    if (!element) return;

    if (focusTimer.current !== null) {
      window.clearTimeout(focusTimer.current);
      focusTimer.current = null;
    }

    element.interpolationDecay = 120;
    element.cameraTarget = "auto auto auto";
    element.cameraOrbit = "35deg 72deg auto";
    element.fieldOfView = "30deg";
  }, [resetToken, module.id]);

  useEffect(() => {
    const element = viewer.current as ModelViewerInstance | null;
    if (!element) return;

    const handleVisibility = (event: Event) => {
      const hotspot = event.target as HTMLElement;

      console.log(
        "hotspot:",
        hotspot,
        "visible:",
        hotspot.hasAttribute("data-visible"),
      );
    };

    element.addEventListener("hotspot-visibility", handleVisibility);

    return () => {
      element.removeEventListener("hotspot-visibility", handleVisibility);
    };
  }, []);

  useEffect(
    () => () => {
      if (focusTimer.current !== null) window.clearTimeout(focusTimer.current);
    },
    [],
  );

  useEffect(() => {
    if (hotspotsVisible || focusTimer.current === null) return;
    window.clearTimeout(focusTimer.current);
    focusTimer.current = null;
  }, [hotspotsVisible]);

  const focusHotspot = (hotspot: Hotspot) => {
    if (focusTimer.current !== null) {
      window.clearTimeout(focusTimer.current);
      focusTimer.current = null;
    }

    if (activeHotspot === hotspot.id) {
      onHotspot(null);
      return;
    }

    const element = viewer.current as ModelViewerInstance | null;
    if (!element) {
      onHotspot(hotspot.id);
      return;
    }

    const orbit = element.getCameraOrbit();
    element.interpolationDecay = 120;
    element.cameraTarget = hotspot.position;
    element.cameraOrbit = `${orbit.theta}rad ${orbit.phi}rad 72%`;
    onHotspot(null);

    focusTimer.current = window.setTimeout(() => {
      onHotspot(hotspot.id);
      focusTimer.current = null;
    }, 420);
  };

  return (
    <div className="model-stage real-model-stage">
      {module.panoramas && (
        <Panorama
          panoramaVisible={panoramaVisible}
          panoramaImage={module.panoramas[0].path}
          hotspots={module.panoramas[0].panoramaHotspots}
          onClose={() => {
            setPanoramaVisible(false);
            onPanoramaChange(true);
          }}
        />
      )}
      <div className="stage-grid" />
      <div
        className={`model-loader ${isLoading ? "is-visible" : "is-hidden"}`}
        role="status"
        aria-live="polite"
        aria-hidden={!isLoading}
      >
        <span className="model-loader-spinner" />
        <span>Загрузка 3D-модели</span>
      </div>
      <ModelViewerElement
        ref={viewer}
        className={isLoading ? "is-loading" : "is-loaded"}
        src={`/training-content/${module.id}/${module.model}`}
        alt={`3D-модель: ${module.name}`}
        camera-controls="true"
        disable-pan="true"
        interaction-prompt="none"
        reveal="auto"
        shadow-intensity="1.2"
        shadow-softness="0.9"
        exposure="0.9"
        environment-image="neutral"
        camera-orbit="35deg 72deg auto"
        min-camera-orbit="auto auto 55%"
        max-camera-orbit="auto auto 220%"
      >
        {hotspotsVisible &&
          module.hotspots.map((hotspot) => (
            <button
              key={hotspot.id}
              slot={`hotspot-${hotspot.id}`}
              data-position={hotspot.position}
              data-normal={hotspot.normal}
              data-visibility-attribute="visible"
              className={`mv-hotspot ${activeHotspot === hotspot.id ? "is-active" : ""}`}
              onClick={() => focusHotspot(hotspot)}
            >
              {hotspot.isPanorama ? (
                <span
                  className="mv-hotspot-dot"
                  style={{
                    width: "30px",
                    height: "30px",
                    borderRadius: "5px",
                    fontSize: "14px",
                  }}
                >
                  П
                </span>
              ) : (
                <span className="mv-hotspot-dot">•</span>
              )}

              {activeHotspot === hotspot.id && (
                <span className="mv-hotspot-callout">
                  <strong>{hotspot.label}</strong>

                  {hotspot.isPanorama ? (
                    <a
                      className="model-action"
                      style={{
                        padding: "10px",
                        border: "1.5px solid var(--accent)",
                      }}
                      onClick={(event) => {
                        event.stopPropagation();
                        showPanorama();
                      }}
                    >
                      Нажмите, чтобы открыть панораму
                    </a>
                  ) : (
                    <small>{hotspot.description}</small>
                  )}
                  <span>Нажмите, чтобы закрыть</span>
                </span>
              )}
            </button>
          ))}
      </ModelViewerElement>
    </div>
  );
}

export function ModelOverview(props: ModelOverviewProps) {
  return props.module.model ? (
    <GlbViewer key={props.module.id} {...props} />
  ) : (
    <PlaceholderViewer
      key={`${props.module.id}-${props.resetToken}`}
      {...props}
    />
  );
}
