import { useEffect, useMemo, useState } from "react";
import { CivicApiError, api } from "../../lib/api";
import type { DashboardSummary, PublicTicketRow, TicketStatus } from "../../lib/types";
import { GhmcChoropleth, type WardGeoJson } from "../../components/charts/GhmcChoropleth";

const STATUS_FILTERS: Array<{ id: TicketStatus | "all"; labelEn: string; labelHi: string }> = [
  { id: "all", labelEn: "All", labelHi: "सभी" },
  { id: "pending", labelEn: "Pending", labelHi: "लंबित" },
  { id: "in_progress", labelEn: "In Progress", labelHi: "प्रगति पर" },
  { id: "completed", labelEn: "Completed", labelHi: "पूर्ण" },
];
const WARD_PREVIEW_COUNT = 10;
const TICKET_PREVIEW_COUNT = 12;

function relativeDate(value: string, hindi: boolean): string {
  const date = new Date(value);
  const diffMs = Date.now() - date.getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (days <= 0) return hindi ? "आज" : "Today";
  if (days === 1) return hindi ? "1 दिन पहले" : "1 day ago";
  return hindi ? `${days} दिन पहले` : `${days} days ago`;
}

function statusClass(status: TicketStatus): string {
  return `status-badge status-badge--${status}`;
}

function statusLabel(status: TicketStatus, hindi: boolean): string {
  if (hindi) {
    if (status === "pending") return "लंबित";
    if (status === "in_progress") return "प्रगति पर";
    return "पूर्ण";
  }
  if (status === "pending") return "Pending";
  if (status === "in_progress") return "In Progress";
  return "Completed";
}

export function DashboardPage({ hindi, onTrack }: { hindi: boolean; onTrack: () => void }) {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [tickets, setTickets] = useState<PublicTicketRow[]>([]);
  const [wardMap, setWardMap] = useState<WardGeoJson | null>(null);
  const [filter, setFilter] = useState<TicketStatus | "all">("all");
  const [showAllWards, setShowAllWards] = useState(false);
  const [showAllTickets, setShowAllTickets] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    let active = true;
    setBusy(true);
    setError("");
    Promise.all([
      api.dashboardSummary(),
      api.dashboardTickets(undefined, 50),
      api.dashboardWardMap(),
    ])
      .then(([nextSummary, nextTickets, nextMap]) => {
        if (!active) return;
        setSummary(nextSummary);
        setTickets(nextTickets);
        setWardMap(nextMap as WardGeoJson);
      })
      .catch((caught) => {
        if (!active) return;
        setError(
          caught instanceof CivicApiError
            ? caught.message
            : hindi
              ? "डैशबोर्ड लोड नहीं हो सका।"
              : "The dashboard could not be loaded.",
        );
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [hindi]);

  useEffect(() => {
    api
      .dashboardTickets(filter === "all" ? undefined : filter, 50)
      .then(setTickets)
      .catch(() => undefined);
  }, [filter]);

  useEffect(() => {
    setShowAllTickets(false);
  }, [filter]);

  const topWards = useMemo(() => (summary?.wards ?? []).slice(0, 3), [summary]);
  const visibleWards = useMemo(() => {
    const wards = summary?.wards ?? [];
    return showAllWards ? wards : wards.slice(0, WARD_PREVIEW_COUNT);
  }, [showAllWards, summary?.wards]);
  const visibleTickets = useMemo(
    () => (showAllTickets ? tickets : tickets.slice(0, TICKET_PREVIEW_COUNT)),
    [showAllTickets, tickets],
  );
  const wardTotal = summary?.wards.length ?? 0;
  const hasMoreWards = wardTotal > WARD_PREVIEW_COUNT;
  const hasMoreTickets = tickets.length > TICKET_PREVIEW_COUNT;

  return (
    <>
      <p className="breadcrumb">
        {hindi ? "मुख्य पृष्ठ" : "Home"} / {hindi ? "नागरिक सेवाएँ" : "Citizen services"} /{" "}
        <strong>{hindi ? "शहर डैशबोर्ड" : "City dashboard"}</strong>
      </p>
      <header className="page-title">
        <div>
          <h1>{hindi ? "खुला नागरिक ट्रैकिंग बोर्ड" : "Open civic tracking board"}</h1>
          <p>
            {hindi
              ? "इस प्रोटोटाइप में दर्ज हर शिकायत यहाँ दिखती है ताकि वार्ड हॉटस्पॉट और विभागीय प्रतिक्रिया दिख सके। यह लाइव GHMC सिस्टम नहीं है।"
              : "Every reported issue in this prototype is listed here so citizens can see ward hotspots and department response. This is not a live GHMC system — it shows how transparency creates accountability."}
          </p>
        </div>
      </header>
      <p className="notice-banner dashboard-banner" role="note">
        {hindi
          ? "प्रदर्शन डेटा — OSM-आधारित ~150 GHMC वार्ड सीमाएँ। कोई लाइव GHMC इनबॉक्स जुड़ा नहीं है।"
          : "Demonstration data — OSM-derived ~150 GHMC ward boundaries. No live GHMC inbox is connected."}
      </p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {busy && !summary ? (
        <p className="dashboard-loading">{hindi ? "डैशबोर्ड लोड हो रहा है…" : "Loading dashboard…"}</p>
      ) : summary ? (
        <>
          <GhmcChoropleth data={wardMap} hindi={hindi} />
          <section className="dashboard-stats" aria-label={hindi ? "सारांश" : "Summary"}>
            <article className="dashboard-stat-card">
              <span>{hindi ? "कुल मुद्दे" : "Total issues"}</span>
              <strong>{summary.total}</strong>
            </article>
            <article className="dashboard-stat-card">
              <span>{hindi ? "लंबित" : "Pending"}</span>
              <strong>{summary.pending}</strong>
            </article>
            <article className="dashboard-stat-card">
              <span>{hindi ? "प्रगति पर" : "In progress"}</span>
              <strong>{summary.in_progress}</strong>
            </article>
            <article className="dashboard-stat-card">
              <span>{hindi ? "पूर्ण" : "Completed"}</span>
              <strong>{summary.completed}</strong>
            </article>
            <p className="dashboard-updated">
              {hindi ? "अंतिम अपडेट" : "Last updated"}: {new Date(summary.last_updated).toLocaleString("en-IN")}
            </p>
          </section>

          <section className="dashboard-dept-grid">
            <h2>{hindi ? "विभाग कंसोल" : "Department console"}</h2>
            <div className="dashboard-dept-cards">
              {summary.departments.map((dept) => (
                <article key={dept.department} className="dashboard-dept-card">
                  <h3>{dept.department}</h3>
                  <dl>
                    <div>
                      <dt>{hindi ? "कुल" : "Total"}</dt>
                      <dd>{dept.total}</dd>
                    </div>
                    <div>
                      <dt>{hindi ? "लंबित" : "Pending"}</dt>
                      <dd>{dept.pending}</dd>
                    </div>
                    <div>
                      <dt>{hindi ? "प्रगति" : "In progress"}</dt>
                      <dd>{dept.in_progress}</dd>
                    </div>
                    <div>
                      <dt>{hindi ? "पूर्ण" : "Completed"}</dt>
                      <dd>{dept.completed}</dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          </section>

          <section className="dashboard-ward-table-wrap">
            <div className="dashboard-section-head">
              <h2>{hindi ? "वार्ड हॉटस्पॉट" : "Ward hotspots"}</h2>
              <p>
                {hindi
                  ? showAllWards
                    ? `सभी ${wardTotal} वार्ड`
                    : `शीर्ष ${Math.min(WARD_PREVIEW_COUNT, wardTotal)} में से ${wardTotal} वार्ड`
                  : showAllWards
                    ? `All ${wardTotal} wards`
                    : `Top ${Math.min(WARD_PREVIEW_COUNT, wardTotal)} of ${wardTotal} wards`}
              </p>
            </div>
            <div className={`dashboard-table-scroll${showAllWards ? " dashboard-table-scroll--expanded" : ""}`}>
              <table className="dashboard-ward-table">
                <thead>
                  <tr>
                    <th>{hindi ? "वार्ड" : "Ward"}</th>
                    <th>{hindi ? "कुल" : "Total"}</th>
                    <th>{hindi ? "लंबित" : "Pending"}</th>
                    <th>{hindi ? "प्रगति" : "In progress"}</th>
                    <th>{hindi ? "पूर्ण" : "Completed"}</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleWards.map((ward) => (
                    <tr key={`${ward.ward_id}-${ward.ward_name}`} className={topWards.includes(ward) ? "dashboard-ward-hot" : undefined}>
                      <th scope="row">
                        {ward.ward_name}
                        {ward.ward_id !== ward.ward_name.toLowerCase().replace(/\s+/g, "-") ? ` (${ward.ward_id})` : ""}
                      </th>
                      <td>{ward.total}</td>
                      <td>{ward.pending}</td>
                      <td>{ward.in_progress}</td>
                      <td>{ward.completed}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {hasMoreWards && (
              <p className="dashboard-table-toggle">
                <button type="button" onClick={() => setShowAllWards((value) => !value)}>
                  {showAllWards
                    ? hindi
                      ? "कम दिखाएँ"
                      : "Show fewer wards"
                    : hindi
                      ? `सभी ${wardTotal} वार्ड दिखाएँ`
                      : `Show all ${wardTotal} wards`}
                </button>
              </p>
            )}
          </section>

          <section className="dashboard-ticket-table-wrap">
            <div className="dashboard-ticket-head">
              <div className="dashboard-section-head">
                <h2>{hindi ? "हाल की शिकायतें" : "Recent tickets"}</h2>
                <p>
                  {hindi
                    ? showAllTickets
                      ? `सभी ${tickets.length} दिख रही हैं`
                      : `हाल की ${Math.min(TICKET_PREVIEW_COUNT, tickets.length)} शिकायतें`
                    : showAllTickets
                      ? `Showing all ${tickets.length}`
                      : `Latest ${Math.min(TICKET_PREVIEW_COUNT, tickets.length)} reports`}
                </p>
              </div>
              <div className="dashboard-filter-chips" role="tablist" aria-label={hindi ? "स्थिति फ़िल्टर" : "Status filters"}>
                {STATUS_FILTERS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={filter === item.id ? "active" : undefined}
                    onClick={() => setFilter(item.id)}
                  >
                    {hindi ? item.labelHi : item.labelEn}
                  </button>
                ))}
              </div>
            </div>
            <div className={`dashboard-table-scroll${showAllTickets ? " dashboard-table-scroll--expanded" : ""}`}>
              <table className="dashboard-ticket-table">
                <thead>
                  <tr>
                    <th>{hindi ? "संदर्भ" : "Ref"}</th>
                    <th>{hindi ? "सेवा" : "Service"}</th>
                    <th>{hindi ? "वार्ड" : "Ward"}</th>
                    <th>{hindi ? "विभाग" : "Department"}</th>
                    <th>{hindi ? "स्थिति" : "Status"}</th>
                    <th>{hindi ? "दर्ज" : "Reported"}</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleTickets.map((ticket) => (
                    <tr key={`${ticket.ref_masked}-${ticket.reported_at}`}>
                      <td>{ticket.ref_masked}</td>
                      <td>{ticket.service_label}</td>
                      <td>{ticket.ward_name}</td>
                      <td>{ticket.department}</td>
                      <td>
                        <span className={statusClass(ticket.status)}>{statusLabel(ticket.status, hindi)}</span>
                      </td>
                      <td>{relativeDate(ticket.reported_at, hindi)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {hasMoreTickets && (
              <p className="dashboard-table-toggle">
                <button type="button" onClick={() => setShowAllTickets((value) => !value)}>
                  {showAllTickets
                    ? hindi
                      ? "कम दिखाएँ"
                      : "Show fewer tickets"
                    : hindi
                      ? `सभी ${tickets.length} शिकायतें दिखाएँ`
                      : `Show all ${tickets.length} tickets`}
                </button>
              </p>
            )}
            <p className="dashboard-track-link">
              <button type="button" className="primary" onClick={onTrack}>
                {hindi ? "अपना अनुरोध ट्रैक करें" : "Track your own request"}
              </button>
            </p>
          </section>
        </>
      ) : null}
    </>
  );
}
