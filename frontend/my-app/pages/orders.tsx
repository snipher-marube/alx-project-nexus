import { useEffect, useState } from "react";

const statusColor = {
  Pending: "text-yellow-600 bg-yellow-100",
  Shipped: "text-blue-600 bg-blue-100",
  Delivered: "text-green-600 bg-green-100",
  Cancelled: "text-red-600 bg-red-100",
};

interface Product {
  id: string;
  title: string;
  image: string;
  price: string;
  quantity: number;
}

interface Order {
  id: string;
  date: string;
  total: number;
  status: "Pending" | "Shipped" | "Delivered" | "Cancelled";
  products?: Product[];
}

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [openDetails, setOpenDetails] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("orders");
    if (stored) setOrders(JSON.parse(stored));
  }, []);

  const toggleDetails = (orderId: string) => {
    setOpenDetails((prev) => (prev === orderId ? null : orderId));
  };

  return (
    <main className="bg-slate-100 min-h-screen py-12 px-6 text-black">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">All Orders</h1>

        {orders.length === 0 ? (
          <p className="text-gray-600">You have no orders yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border rounded shadow-sm">
              <thead className="bg-gray-100 text-left">
                <tr>
                  <th className="p-4 text-sm font-semibold">Order ID</th>
                  <th className="p-4 text-sm font-semibold">Date</th>
                  <th className="p-4 text-sm font-semibold">Total</th>
                  <th className="p-4 text-sm font-semibold">Status</th>
                  <th className="p-4 text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <>
                    <tr key={order.id} className="border-t hover:bg-gray-50">
                      <td className="p-4 text-sm">{order.id}</td>
                      <td className="p-4 text-sm">{order.date}</td>
                      <td className="p-4 text-sm">
                        KSh {order.total.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="p-4 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor[order.status]}`}>{order.status}</span>
                      </td>
                      <td className="p-4 text-sm">
                        <button
                          className="text-blue-600 hover:underline text-xs"
                          onClick={() => toggleDetails(order.id)}
                        >
                          {openDetails === order.id ? "Hide Details" : "View Details"}
                        </button>
                      </td>
                    </tr>

                    {openDetails === order.id && order.products && (
                      <tr key={`${order.id}-details`}>
                        <td colSpan={5} className="p-4 bg-gray-50">
                          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
                            {order.products.map((product) => (
                              <div
                                key={product.id}
                                className="bg-white rounded-lg shadow p-4 flex items-center gap-4"
                              >
                                <img
                                  src={product.image}
                                  alt={product.title}
                                  className="w-16 h-16 object-cover rounded"
                                />
                                <div>
                                  <h3 className="font-semibold text-sm text-gray-800">{product.title}</h3>
                                  <p className="text-green-600 text-sm font-bold">{product.price}</p>
                                  <p className="text-gray-500 text-xs">Qty: {product.quantity}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
