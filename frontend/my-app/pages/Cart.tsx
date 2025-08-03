
/* eslint-disable @next/next/no-img-element */
import { useCart } from "@/context/CartContext";
import Link from "next/link";

export default function CartPage() {
  const { cart, removeFromCart, clearCart } = useCart();

  const totalPrice = cart.reduce((sum, item) => {
 
    const price = typeof item.price === "string"
      ? parseFloat(item.price.replace(/[^\d.]/g, ""))
      : item.price;

    return sum + price * item.quantity;
  }, 0);

  return (
    <main className="min-h-screen text-black py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Your Cart</h1>

        {cart.length === 0 ? (
          <p className="text-gray-600">Your cart is empty.</p>
        ) : (
          <div className="space-y-6">
            {cart.map((item) => (
              <div
                key={item.id}
                className="bg-neutral-50 rounded-lg shadow p-4 flex items-center gap-4"
              >
                <img
                  src={item.primary_image.image_url}
                  alt={item.primary_image.image_url}
                  className="w-24 h-24 object-cover rounded"
                />
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-800">{item.name}</h2>
                  
                  <p className="text-green-600 font-bold">
                    ${typeof item.price === "string" ? parseFloat(item.price).toFixed(2) : item.price.toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-500">Quantity: {item.quantity}</p>
                </div>
                <button
                  onClick={() => removeFromCart(item.id)}
                  className="text-red-600 hover:text-red-800 font-bold"
                >
                  ✕
                </button>
              </div>
            ))}

            <div className="bg-neutral-50 rounded-lg shadow p-4 flex justify-between items-center">
              <p className="text-xl font-semibold text-gray-800">
                Total: ${totalPrice.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </p>
              <Link href="/Checkout">
                <button className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                  Proceed to Checkout
                </button>
              </Link>
            </div>

            <button
              onClick={clearCart}
              className="text-sm text-white hover:text-red-600 mt-4 bg-red-500 py-3 px-6 rounded"
            >
              Clear Cart
            </button>
          </div>
        )}
      </div>
    </main>
  );
}