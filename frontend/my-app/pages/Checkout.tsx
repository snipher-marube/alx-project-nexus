/* eslint-disable @next/next/no-img-element */
import { useCart } from "@/context/CartContext";
import { useRouter } from "next/router";

export default function CheckoutPage() {
  const { cart, clearCart } = useCart();
  const router = useRouter();

  const handleCheckout = () => {
    const existingOrders = JSON.parse(localStorage.getItem("orders") || "[]");
    const orderId = `ORD${Date.now().toString().slice(-6)}`;

    const total = cart.reduce((sum, item) => {
      const price = parseFloat(item.price.replace(/[^\d.]/g, ""));
      return sum + price * item.quantity;
    }, 0);

    const order = {
      id: orderId,
      date: new Date().toISOString().split("T")[0],
      total: parseFloat(total.toFixed(2)),
      status: "Pending",
      products: cart,
    };

    localStorage.setItem("orders", JSON.stringify([...existingOrders, order]));
    clearCart();
    router.push("/orders");
  };

  return (
    <main className="min-h-screen bg-slate-100 py-12 px-4 sm:px-8 lg:px-24 text-black">
      <h1 className="text-3xl font-bold text-center mb-8">Checkout</h1>

      {cart.length === 0 ? (
        <p className="text-center text-gray-600">Your cart is empty.</p>
      ) : (
        <div className="space-y-6 max-w-3xl mx-auto">
          {cart.map((item) => (
            <div
              key={item.id}
              className="bg-white p-4 rounded-xl shadow flex items-center gap-4"
            >
              <img
                src={item.image}
                alt={item.title}
                className="w-20 h-20 object-cover rounded"
              />
              <div>
                <h2 className="font-semibold text-lg text-gray-800">{item.title}</h2>
                <p className="text-sm text-gray-500">
                  {item.quantity} x {item.price}
                </p>
              </div>
            </div>
          ))}

          <div className="text-right">
            <button
              onClick={handleCheckout}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Place Order
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
