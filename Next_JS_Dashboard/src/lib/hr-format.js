/**
 * Human-readable labels for API enum values (candidate stage / status).
 */

const STAGE_LABELS = {
  submitted: 'Submitted',
  parsed: 'Parsed',
  scored: 'Scored',
  shortlisted: 'Shortlisted',
  interviewed: 'Interviewed',
  final: 'Final',
};

const STATUS_LABELS = {
  active: 'Active',
  rejected: 'Rejected',
  waitlisted: 'Waitlisted',
  selected: 'Selected',
};

export function formatStage(value) {
  if (!value) return '—';
  const key = String(value).toLowerCase();
  return STAGE_LABELS[key] ?? value;
}

export function formatStatus(value) {
  if (!value) return '—';
  const key = String(value).toLowerCase();
  return STATUS_LABELS[key] ?? value;
}

export function stageBadgeClass(stage) {
  const key = String(stage || '').toLowerCase();
  const map = {
    submitted: 'bg-slate-100 text-slate-800 ring-slate-500/15',
    parsed: 'bg-sky-100 text-sky-900 ring-sky-500/20',
    scored: 'bg-indigo-100 text-indigo-900 ring-indigo-500/20',
    shortlisted: 'bg-emerald-100 text-emerald-900 ring-emerald-500/20',
    interviewed: 'bg-violet-100 text-violet-900 ring-violet-500/20',
    final: 'bg-amber-100 text-amber-950 ring-amber-500/25',
  };
  return map[key] || 'bg-muted text-muted-foreground ring-border';
}

export function statusBadgeClass(status) {
  const key = String(status || '').toLowerCase();
  const map = {
    active: 'bg-blue-100 text-blue-900 ring-blue-500/20',
    rejected: 'bg-red-100 text-red-900 ring-red-500/20',
    waitlisted: 'bg-amber-100 text-amber-950 ring-amber-500/25',
    selected: 'bg-emerald-100 text-emerald-900 ring-emerald-500/20',
  };
  return map[key] || 'bg-muted text-muted-foreground ring-border';
}
