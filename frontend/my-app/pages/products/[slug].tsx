/* eslint-disable @next/next/no-img-element */

import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useCart } from "@/context/CartContext";
import { Product } from "@/interface/Products";

export default function ProductDetailPage() {
  const router = useRouter();
  const { slug } = router.query;
  const { addToCart } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) {
      fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/${slug}`)
        .then((res) => {
          if (!res.ok) throw new Error("Product not found");
          return res.json();
        })
        .then((data) => {
          if (!data || !data.id || !data.name) throw new Error("Invalid product data");
          setProduct(data);
        })
        .catch(() => {
          setProduct(null);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [slug]);

  if (loading) return <p className="p-6 text-gray-500">Loading product...</p>;
  if (!product) return <p className="p-6 text-red-500">Product not found.</p>;

  return (
    <main className="p-6 bg-gray-100 min-h-screen text-black">
      <div className="max-w-4xl mx-auto bg-white rounded shadow-md p-6 flex flex-col md:flex-row gap-8">
        <img
          src={product.primary_image}
          alt={product.name}
          className="w-full md:w-1/2 h-80 object-cover rounded"
        />
        <div className="flex-1">
          <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
          <p className="text-green-600 font-bold text-xl mb-4">{product.price}</p>
          <p className="text-gray-700 mb-6">{product.description}</p>
          <button
            className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
            onClick={() => {
              addToCart(product);
              alert("Added to cart!");
            }}
          >
            Add to Cart
          </button>

                </div>
              </div>
            </main>
          );
        }


        {/*
export const dummyProducts: Product[] = [
  {
    id: 1,
    name: "Smartphone",
    primary_image: "https://via.placeholder.com/200",
    price: "$299.99",
    description: "Latest model with high definition display and powerful chip.",
  },
  {
    id: 2,
    name: "Laptop",
    primary_image: "https://via.placeholder.com/200",
    price: "$899.99",
    description: "High performance laptop for gaming and productivity.",
  },
  {
    id: 3,
    name: "Headphones",
    primary_image: "https://via.placeholder.com/200",
    price: "$199.99",
    description: "Noise-cancelling headphones with superior sound quality.",
  },
  {
    id: 4,
    name: "Smartwatch",
    primary_image: "https://via.placeholder.com/200",
    price: "$149.99",
    description: "Track your fitness and stay connected on the go.",
  },
  {
    id: 5,
    name: "Wrist Watch",
    primary_image: "https://via.placeholder.com/200",
    price: "$120.00",
    description: "Elegant wrist watch with classic design.",
  },
];
/
*/}

function addToCart(product: Product) {
  const existing = JSON.parse(localStorage.getItem("cart") || "[]");
  existing.push(product);
  localStorage.setItem("cart", JSON.stringify(existing));
  alert("Added to cart!");
}
