import { useEffect, useState } from 'react';
import { api } from '../api/client';
import Alert from '../components/Alert';
import Loading from '../components/Loading';
import Modal from '../components/Modal';
import PageHeader from '../components/PageHeader';

const emptyForm = {
  sku: '',
  name: '',
  description: '',
  price: '',
  quantity_in_stock: '0',
};

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  async function loadProducts() {
    try {
      setLoading(true);
      const data = await api.products.list();
      setProducts(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  function openCreateModal() {
    setEditingProduct(null);
    setForm(emptyForm);
    setModalOpen(true);
    setSuccess('');
  }

  function openEditModal(product) {
    setEditingProduct(product);
    setForm({
      sku: product.sku,
      name: product.name,
      description: product.description || '',
      price: String(product.price),
      quantity_in_stock: String(product.quantity_in_stock),
    });
    setModalOpen(true);
    setSuccess('');
  }

  function closeModal() {
    setModalOpen(false);
    setEditingProduct(null);
    setForm(emptyForm);
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');

    const payload = {
      sku: form.sku.trim(),
      name: form.name.trim(),
      description: form.description.trim() || null,
      price: Number(form.price),
      quantity_in_stock: Number(form.quantity_in_stock),
    };

    try {
      if (editingProduct) {
        await api.products.update(editingProduct.id, payload);
        setSuccess('Product updated successfully.');
      } else {
        await api.products.create(payload);
        setSuccess('Product created successfully.');
      }
      closeModal();
      await loadProducts();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(product) {
    if (!window.confirm(`Delete product "${product.name}"?`)) return;

    try {
      await api.products.delete(product.id);
      setSuccess('Product deleted successfully.');
      setError('');
      await loadProducts();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <Loading label="Loading products..." />;

  return (
    <div>
      <PageHeader
        title="Products"
        subtitle="Add, view, update, and delete products"
        action={
          <button type="button" className="btn btn-primary" onClick={openCreateModal}>
            + Add Product
          </button>
        }
      />

      <Alert message={error} />
      <Alert message={success} type="success" />

      <section className="panel">
        {products.length === 0 ? (
          <p className="empty-state">No products yet. Add your first product to get started.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.sku}</td>
                    <td>{product.name}</td>
                    <td>${Number(product.price).toFixed(2)}</td>
                    <td>{product.quantity_in_stock}</td>
                    <td className="actions-cell">
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => openEditModal(product)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(product)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {modalOpen && (
        <Modal title={editingProduct ? 'Update Product' : 'Add Product'} onClose={closeModal}>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>
              SKU
              <input name="sku" value={form.sku} onChange={handleChange} required />
            </label>
            <label>
              Product Name
              <input name="name" value={form.name} onChange={handleChange} required />
            </label>
            <label>
              Price
              <input
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={handleChange}
                required
              />
            </label>
            <label>
              Quantity in Stock
              <input
                name="quantity_in_stock"
                type="number"
                min="0"
                value={form.quantity_in_stock}
                onChange={handleChange}
                required
              />
            </label>
            <label className="full-width">
              Description
              <textarea
                name="description"
                rows="3"
                value={form.description}
                onChange={handleChange}
              />
            </label>
            <div className="form-actions full-width">
              <button type="button" className="btn btn-secondary" onClick={closeModal}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Saving...' : editingProduct ? 'Update Product' : 'Add Product'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
