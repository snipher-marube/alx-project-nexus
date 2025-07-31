/* eslint-disable @next/next/no-img-element */
import React, { useState } from "react";
import Link from "next/link";
import Image from 'next/image';
import SearchBar from "../components/common/SearchBar";
import { useCart } from "@/context/CartContext";
import { ProductList, ProductsResponse } from "@/interface/Products";



export async function getServerSideProps() {
  try {
    const res = await fetch('https://alx-project-nexus-psi.vercel.app/api/v1/products');
    const data: ProductsResponse = await res.json();
    const products: ProductList[] = data.results;

    return {
      props: {
        products,
      },
    };
  } catch(error) {
    console.error("Failed to fetch products:", error);
    return {
      props: {
        products: [], // fallback
      },
    };
  }
}


export default function ProductsPage({products}: {products: ProductList[]}) {
  const [filteredProducts, setFilteredProducts] = useState(products);
  const { addToCart } = useCart();

  const handleSearch = (query: string) => {
    const filtered = products.filter((product) => 
      product.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredProducts(filtered);
  };

  const handleAddToCart = (product: ProductList) => {
    addToCart(product);
  };

  return (
    <main className="min-h-screen py-12 px-6 text-black">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">Our Products</h2>

        <div className="flex justify-center mb-10">
          <SearchBar onSearch={handleSearch} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {Array.isArray(products) && filteredProducts.map((product) => (
            <Link key={product.id} href={`/products/${product.slug}`} className="block">
              <div className="relative bg-white rounded-lg shadow p-4 flex flex-col items-center text-center hover:shadow-md transition">
                <Image
                  src={product.primary_image.image_url}
                  alt={product.name} width={400} height={450}
                  className="w-full h-40 object-cover rounded mb-4"
                />
                <h3 className="text-lg font-semibold text-gray-800 mb-1">{product.name}</h3>
                <p className="text-green-600 font-bold mb-2">${product.price}</p>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleAddToCart(product);
                    alert("Added to cart!");
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
