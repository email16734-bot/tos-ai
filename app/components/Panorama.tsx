import { useEffect, useRef } from "react";
import { Viewer } from "@photo-sphere-viewer/core";
import { MarkersPlugin } from "@photo-sphere-viewer/markers-plugin";

import "@photo-sphere-viewer/core/index.css";
import "@photo-sphere-viewer/markers-plugin/index.css";

type PanoramaHotspot = {
  id: string;
  label: string;
  description: string;
  position: {
    yaw: string;
    pitch: string;
  };
};

type PanoramaProps = {
  panoramaVisible: boolean;
  panoramaImage: string;
  hotspots?: PanoramaHotspot[];
  onClose: () => void;
};

export function Panorama({
  panoramaVisible,
  panoramaImage,
  hotspots = [],
  onClose,
}: PanoramaProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);

  useEffect(() => {
    if (!containerRef.current || !panoramaVisible || !panoramaImage) {
      return;
    }

    const viewer = new Viewer({
      container: containerRef.current,
      panorama: panoramaImage,

      navbar: [
        "zoom",
        "fullscreen",
        {
          id: "close-panorama",
          title: "Закрыть панораму",
          content: `
    <svg
      viewBox="0 0 24 24"
      width="20"
      height="20"
      aria-hidden="true"
    >
      <path
        d="M6 6L18 18M18 6L6 18"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
  `,
          className: "psv-button",
          onClick() {
            onClose();
          },
        },
      ],

      plugins: [
        MarkersPlugin.withConfig({
          markers: hotspots.map((hotspot) => ({
            id: hotspot.id,
            position: hotspot.position,
            circle: 20,
            style: {
              fill: "#ff3b30",
              stroke: "#ffffff",
              strokeWidth: "4px",
            },
            tooltip: hotspot.label,
          })),
        }),
      ],
    });

    viewerRef.current = viewer;

    const markersPlugin = viewer.getPlugin(MarkersPlugin);

    markersPlugin.addEventListener("select-marker", ({ marker }) => {
      console.log("Нажат маркер:", marker.id);
    });

    return () => {
      viewer.destroy();
      viewerRef.current = null;
    };
  }, [panoramaVisible, panoramaImage, hotspots]);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "82%",
        zIndex: 9999,
        display: panoramaVisible ? "block" : "none",
      }}
    />
  );
}
