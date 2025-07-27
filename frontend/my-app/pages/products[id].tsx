/* eslint-disable @next/next/no-img-element */
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { allProducts } from "../data/Categories";
import { useCart } from "@/context/CartContext";

export default function ProductDetail() {
  const router = useRouter();
  const { id } = router.query;
  const { addToCart } = useCart();
  const [product, setProduct] = useState<any>(null);

  useEffect(() => {
    if (id) {
      const found = allProducts.find((p) => p.id === id);
      setProduct(found || null);
    }
  }, [id]);

  if (!product) {
    return (
      <div className="p-6 text-center text-gray-600">
        <p>Product not found.</p>
      </div>
    );
  }

  return (
    <main className="p-6 bg-slate-100 min-h-screen text-black">
      <div className="max-w-4xl mx-auto bg-white rounded shadow p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <img
          src={product.image}
          alt={product.title}
          className="w-full h-80 object-cover rounded"
        />

        <div>
          <h1 className="text-2xl font-bold mb-4">{product.title}</h1>
          <p className="text-green-600 font-bold text-xl mb-4">{product.price}</p>
          <p className="text-gray-700 mb-6">
            High definition with the latest chip set . (Add real description here.)
          </p>
          <button
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            onClick={() => addToCart(product)}
          >
            Add to Cart
          </button>
        </div>
      </div>
    </main>
  );
}

export const dummyData = allProducts;