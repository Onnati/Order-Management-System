import { useEffect, useState } from 'react';
import { api } from '../api/client';
import Alert from '../components/Alert';
import Loading from '../components/Loading';
import Modal from '../components/Modal';
import PageHeader from '../components/PageHeader';

const emptyForm = {
  full_name: '',
  email: '',
  phone: '',
};

export default function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await api.customers.list();
      setCustomers(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  function openCreateModal() {
    setForm(emptyForm);
    setModalOpen(true);
    setSuccess('');
  }

  function closeModal() {
    setModalOpen(false);
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

    try {
      await api.customers.create({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
      });
      setSuccess('Customer created successfully.');
      closeModal();
      await loadCustomers();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(customer) {
    if (!window.confirm(`Delete customer "${customer.full_name}"?`)) return;

    try {
      await api.customers.delete(customer.id);
      setSuccess('Customer deleted successfully.');
      setError('');
      await loadCustomers();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <Loading label="Loading customers..." />;

  return (
    <div>
      <PageHeader
        title="Customers"
        subtitle="Add, view, and delete customers"
        action={
          <button type="button" className="btn btn-primary" onClick={openCreateModal}>
            + Add Customer
          </button>
        }
      />

      <Alert message={error} />
      <Alert message={success} type="success" />

      <section className="panel">
        {customers.length === 0 ? (
          <p className="empty-state">No customers yet. Add your first customer to get started.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    <td>{customer.full_name}</td>
                    <td>{customer.email}</td>
                    <td>{customer.phone}</td>
                    <td className="actions-cell">
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(customer)}
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
        <Modal title="Add Customer" onClose={closeModal}>
          <form className="form-grid" onSubmit={handleSubmit}>
            <label>
              Full Name
              <input name="full_name" value={form.full_name} onChange={handleChange} required />
            </label>
            <label>
              Email
              <input name="email" type="email" value={form.email} onChange={handleChange} required />
            </label>
            <label className="full-width">
              Phone Number
              <input name="phone" value={form.phone} onChange={handleChange} required />
            </label>
            <div className="form-actions full-width">
              <button type="button" className="btn btn-secondary" onClick={closeModal}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Saving...' : 'Add Customer'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
