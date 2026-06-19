import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import PageHeader from '../components/PageHeader';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [lowStock, setLowStock] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [products, customers, orders, lowStockItems] = await Promise.all([
          api.products.list(),
          api.customers.list(),
          api.orders.list(),
          api.inventory.lowStock(),
        ]);

        setStats({
          products: products.length,
          customers: customers.length,
          orders: orders.length,
        });
        setLowStock(lowStockItems);
        setError('');
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) return <Loading label="Loading dashboard..." />;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Overview of products, customers, orders, and inventory alerts"
      />
      <Alert message={error} />

      <div className="stats-grid">
        <div className="stat-card">
          <p className="stat-label">Total Products</p>
          <p className="stat-value">{stats?.products ?? 0}</p>
          <Link to="/products" className="stat-link">
            Manage products →
          </Link>
        </div>
        <div className="stat-card">
          <p className="stat-label">Total Customers</p>
          <p className="stat-value">{stats?.customers ?? 0}</p>
          <Link to="/customers" className="stat-link">
            Manage customers →
          </Link>
        </div>
        <div className="stat-card">
          <p className="stat-label">Total Orders</p>
          <p className="stat-value">{stats?.orders ?? 0}</p>
          <Link to="/orders" className="stat-link">
            View orders →
          </Link>
        </div>
        <div className="stat-card stat-card-alert">
          <p className="stat-label">Low Stock Products</p>
          <p className="stat-value">{lowStock.length}</p>
          <span className="stat-link">Needs attention</span>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <h3>Low Stock Products</h3>
          <span className="panel-meta">{lowStock.length} items</span>
        </div>

        {lowStock.length === 0 ? (
          <p className="empty-state">All products are above reorder levels.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Product</th>
                  <th>In Stock</th>
                  <th>Reorder Level</th>
                </tr>
              </thead>
              <tbody>
                {lowStock.map((item) => (
                  <tr key={item.id}>
                    <td>{item.product?.sku || '—'}</td>
                    <td>{item.product?.name || '—'}</td>
                    <td>
                      <span className="stock-low">{item.quantity_on_hand}</span>
                    </td>
                    <td>{item.reorder_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
