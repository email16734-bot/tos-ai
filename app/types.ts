export type Theme = "dark" | "light";

export type ModuleTab = "model" | "video" | "text";

export type Hotspot = {
  id: string;
  label: string;
  description: string;
  screen: { x: number; y: number };
  position: string;
  normal: string;
  isPanorama: boolean;
};

export type VideoMaterial = {
  title: string;
  duration: string;
  description: string;
  file?: string;
};

export type TextMaterial = {
  title: string;
  type: string;
  readTime: string;
  description: string;
  file: string;
  pages: number;
};

export type Panorama = {
  id: string;
  path: string;
  panoramaHotspots: PanoramaHotspot[];
};

export type PanoramaHotspot = {
  id: string;
  label: string;
  description: string;
  position: {
    yaw: string;
    pitch: string;
  };
};

export type ModuleData = {
  id: string;
  name: string;
  sklon: string;
  shortName: string;
  category: string;
  subcategory: string;
  description: string;
  cover: string;
  model: string | null;
  hotspots: Hotspot[];
  videos: VideoMaterial[];
  texts: TextMaterial[];
  panoramas: Panorama[];
};
