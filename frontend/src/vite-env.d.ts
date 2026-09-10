/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FORCE_PLAN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
