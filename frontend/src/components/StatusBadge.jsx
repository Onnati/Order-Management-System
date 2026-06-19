const statusStyles = {
  pending: 'badge-warning',
  confirmed: 'badge-info',
  shipped: 'badge-info',
  delivered: 'badge-success',
  cancelled: 'badge-danger',
};

export default function StatusBadge({ status }) {
  const style = statusStyles[status] || 'badge-neutral';
  return <span className={`badge ${style}`}>{status}</span>;
}
