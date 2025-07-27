import React, { useState } from "react";
import Link from "next/link";
import SearchBar from "../components/common/SearchBar";
import { useCart } from "@/context/CartContext";

interface Product {
  id: string;
  title: string;
  image: string;
  price: string;
}

const dummyProducts: Product[] = [
  {
    id: "1",
    title: "Wireless Headphones",
    image: "https://via.placeholder.com/200",
    price: "$59.99",
  },
  {
    id: "2",
    title: "Smartphone",
    image: "https://via.placeholder.com/200",
    price: "$299.99",
  },
  {
    id: "3",
    title: "Sneakers",
    image: "https://via.placeholder.com/200",
    price: "$79.99",
  },
  {
    id: "4",
    title: "Bluetooth Speaker",
    image: "https://via.placeholder.com/200",
    price: "$45.00",
  },
  {
    id: "5",
    title: "Wrist Watch",
    image: "https://via.placeholder.com/200",
    price: "$120.00",
  },
];

export default function ProductsPage() {
  const [products, setProducts] = useState(dummyProducts);
  const { addToCart } = useCart();

  const handleSearch = (query: string) => {
    const filtered = dummyProducts.filter((product) =>
      product.title.toLowerCase().includes(query.toLowerCase())
    );
    setProducts(filtered);
  };

  const handleAddToCart = (product: Product) => {
    addToCart(product);
  };

  return (
    <main className="min-h-screen bg-slate-100 py-12 px-6 text-black">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Our Products</h2>

        <div className="flex justify-center mb-10">
          <SearchBar onSearch={handleSearch} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {products.map((product) => (
            <Link key={product.id} href={`/products/${product.id}`} className="block">
              <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center text-center hover:shadow-md transition">
                <img
                  src={product.image}
                  alt={product.title}
                  className="w-full h-40 object-cover rounded mb-4"
                />
                <h3 className="text-lg font-semibold text-gray-800 mb-1">{product.title}</h3>
                <p className="text-green-600 font-bold mb-2">{product.price}</p>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleAddToCart(product);
                  }}
                  className="mt-auto bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                  Add to Cart
                </button>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
