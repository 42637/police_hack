export const logger = {
  info: (msg: string, ...args: any[]) => {
    console.log(`%c[SENTINEL_INFO] ${msg}`, 'color: #06b6d4; font-weight: bold;', ...args);
  },
  warn: (msg: string, ...args: any[]) => {
    console.warn(`%c[SENTINEL_WARN] ${msg}`, 'color: #eab308; font-weight: bold;', ...args);
  },
  error: (msg: string, ...args: any[]) => {
    console.error(`%c[SENTINEL_ERROR] ${msg}`, 'color: #ef4444; font-weight: bold;', ...args);
  }
};
