type DashboardRefreshListener = () => void;

let version = 0;
const listeners = new Set<DashboardRefreshListener>();

export function getDashboardRefreshVersion(): number {
  return version;
}

/** Call after a grievance is registered so open dashboard views can reload. */
export function notifyDashboardUpdated(): void {
  version += 1;
  listeners.forEach((listener) => listener());
}

export function subscribeDashboardUpdated(listener: DashboardRefreshListener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
