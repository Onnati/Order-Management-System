import { useEffect, useState } from 'react';
import { api } from '../api/client';
import Alert from '../components/Alert';
import Loading from '../components/Loading';
import Modal from '../components/Modal';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';

const emptyLineItem = { product_id: '', quantity: '1' };

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [form, setForm] = useState({ customer_id: '', items: [emptyLineItem] });
  const [submitting, setSubmitting] = useState(false);

  async function loadData() {
    try {
      setLoading(true);
      const [ordersData, customersData, productsData] = await Promise.all([
        api.orders.list(),
        api.customers.list(),
        api.products.list(),
      ]);
      setOrders(ordersData);
      setCustomers(customersData);
      setProducts(productsData);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function openCreateModal() {
    setForm({ customer_id: '', items: [emptyLineItem] });
    setCreateModalOpen(true);
    setSuccess('');
  }

  function closeCreateModal() {
    setCreateModalOpen(false);
  }

  async function openDetailModal(order) {
    try {
      const fullOrder = await api.orders.get(order.id);
      setSelectedOrder(fullOrder);
      setDetailModalOpen(true);
    } catch (err) {
      setError(err.message);
    }
  }

  function closeDetailModal() {
    setDetailModalOpen(false);
    setSelectedOrder(null);
  }

  function handleCustomerChange(event) {
    setForm((current) => ({ ...current, customer_id: event.target.value }));
  }

  function handleItemChange(index, field, value) {
    setForm((current) => {
      const items = [...current.items];
      items[index] = { ...items[index], [field]: value };
      return { ...current, items };
    });
  }

  function addLineItem() {
    setForm((current) => ({
      ...current,
      items: [...current.items, { ...emptyLineItem }],
    }));
  }

  function removeLineItem(index) {
    setForm((current) => ({
      ...current,
      items: current.items.filter((_, itemIndex) => itemIndex !== index),
    }));
  }

  async function handleCreateSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    const payload = {
      customer_id: Number(form.customer_id),
      items: form.items.map((item) => ({
        product_id: Number(item.product_id),
        quantity: Number(item.quantity),
      })),
    };

    try {
      await api.orders.create(payload);
      setSuccess('Order created successfully.');
      closeCreateModal();
      await loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCancel(order) {
    if (!window.confirm(`Cancel order ${order.order_number}?`)) return;

    try {
      await api.orders.cancel(order.id);
      setSuccess('Order cancelled successfully.');
      setError('');
      await loadData();
      if (selectedOrder?.id === order.id) {
        const updated = await api.orders.get(order.id);
        setSelectedOrder(updated);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  function getCustomerName(customerId) {
    return customers.find((customer) => customer.id === customerId)?.full_name || `Customer #${customerId}`;
  }

  function getProductName(productId) {
    return products.find((product) => product.id === productId)?.name || `Product #${productId}`;
  }

  if (loading) return <Loading label="Loading orders..." />;

  return (
    <div>
      <PageHeader
        title="Orders"
        subtitle="Create orders, view order history, and inspect order details"
        action={
          <button type="button" className="btn btn-primary" onClick={openCreateModal}>
            + Create Order
          </button>
        }
      />

      <Alert message={error} />
      <Alert message={success} type="success" />

      <section className="panel">
        {orders.length === 0 ? (
          <p className="empty-state">No orders yet. Create your first order to get started.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td>{order.order_number}</td>
                    <td>{getCustomerName(order.customer_id)}</td>
                    <td>
                      <StatusBadge status={order.status} />
                    </td>
                    <td>${Number(order.total_amount).toFixed(2)}</td>
                    <td>{new Date(order.created_at).toLocaleString()}</td>
                    <td className="actions-cell">
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => openDetailModal(order)}
                      >
                        View
                      </button>
                      {order.status !== 'cancelled' && (
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleCancel(order)}
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {createModalOpen && (
        <Modal title="Create Order" onClose={closeCreateModal}>
          <form className="form-grid" onSubmit={handleCreateSubmit}>
            <label className="full-width">
              Customer
              <select
                name="customer_id"
                value={form.customer_id}
                onChange={handleCustomerChange}
                required
              >
                <option value="">Select a customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.full_name} ({customer.email})
                  </option>
                ))}
              </select>
            </label>

            <div className="full-width line-items">
              <div className="line-items-header">
                <h3>Order Items</h3>
                <button type="button" className="btn btn-secondary btn-sm" onClick={addLineItem}>
                  + Add Item
                </button>
              </div>

              {form.items.map((item, index) => (
                <div className="line-item-row" key={`item-${index}`}>
                  <label>
                    Product
                    <select
                      value={item.product_id}
                      onChange={(event) =>
                        handleItemChange(index, 'product_id', event.target.value)
                      }
                      required
                    >
                      <option value="">Select product</option>
                      {products.map((product) => (
                        <option key={product.id} value={product.id}>
                          {product.name} ({product.sku}) — Stock: {product.quantity_in_stock}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Quantity
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(event) =>
                        handleItemChange(index, 'quantity', event.target.value)
                      }
                      required
                    />
                  </label>
                  {form.items.length > 1 && (
                    <button
                      type="button"
                      className="btn btn-danger btn-sm remove-item-btn"
                      onClick={() => removeLineItem(index)}
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="form-actions full-width">
              <button type="button" className="btn btn-secondary" onClick={closeCreateModal}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Order'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {detailModalOpen && selectedOrder && (
        <Modal title={`Order ${selectedOrder.order_number}`} onClose={closeDetailModal}>
          <div className="order-detail">
            <div className="detail-grid">
              <div>
                <p className="detail-label">Customer</p>
                <p>{getCustomerName(selectedOrder.customer_id)}</p>
              </div>
              <div>
                <p className="detail-label">Status</p>
                <StatusBadge status={selectedOrder.status} />
              </div>
              <div>
                <p className="detail-label">Total Amount</p>
                <p>${Number(selectedOrder.total_amount).toFixed(2)}</p>
              </div>
              <div>
                <p className="detail-label">Created</p>
                <p>{new Date(selectedOrder.created_at).toLocaleString()}</p>
              </div>
            </div>

            <h3>Order Items</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Line Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrder.items.map((item) => (
                    <tr key={item.id}>
                      <td>{getProductName(item.product_id)}</td>
                      <td>{item.quantity}</td>
                      <td>${Number(item.unit_price).toFixed(2)}</td>
                      <td>${Number(item.line_total).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {selectedOrder.status !== 'cancelled' && (
              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={() => handleCancel(selectedOrder)}
                >
                  Cancel Order
                </button>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
