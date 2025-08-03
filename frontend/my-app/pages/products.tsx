/* eslint-disable @next/next/no-img-element */
import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from 'next/image';
import SearchBar from "../components/common/SearchBar";
import { useCart } from "@/context/CartContext";
import { ProductList, ProductsResponse } from "@/interface/Products";



export async function getServerSideProps(context: { query: { page: any; }; }) {
  const currentPage = parseInt(context.query.page ?? '1', 10);

  try {
    const res = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?page=${currentPage}`);
    const data: ProductsResponse = await res.json();
    const next = data.links.next ?? null;
    const previous = data.links.previous ?? null;
    const pageSize = data.page_size;

    return {
      props: {
        products: data.results,
        count: data.count,
        next,
        previous,
        pageSize,
        currentPage: Number(currentPage),
      },
      
    };
  } catch (error) {
    //console.error("Failed to fetch products:", error);
    return {
      props: {
        products: [],
        count: 0,
        next: null,
        previous: null,
        pageSize: null,
        currentPage: 1,
      },
    };
  }
}


export default function ProductsPage({products, count, currentPage, pageSize }: {
  products: ProductList[];
  count: number;
  pageSize: number;
  currentPage: number;
}) {
  
  const [filteredProducts, setFilteredProducts] = useState(products);
  const [message, setMessage] = useState('');
  const { addToCart } = useCart();

  //numbering the pagination based on number of products and products displayed per page
  const totalPages = Math.ceil(count / pageSize);

  //updating each pagination
  useEffect(() => {
    setFilteredProducts(products);
  }, [products]);

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
        setFilteredProducts(products);
        setMessage('');
        return;
      };

    try {
      const res = await fetch('/api/products');
      if (!res.ok) {
        throw new Error(`Failed to fetch: ${res.status}`);
      }

      const data: ProductsResponse = await res.json();
      const productList = data.results;

      const filtered = productList.filter((product) => 
        product.name.toLowerCase().includes(query.toLowerCase())
      );
      if (filtered.length < 1) {
        setFilteredProducts([]);
        setMessage(`No products found for ${query}! `);
      } else {
        setFilteredProducts(filtered);
        setMessage('');
      }
    } catch (error) {
      setMessage('Error fetching products');
    }
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
          {message && <p>{message} </p>}
          {Array.isArray(filteredProducts) && filteredProducts.map((product) => (
            <Link key={product.id} href={`/products/${product.slug}`} className="block">
              <div className="relative bg-neutral-50 rounded-lg shadow p-4 flex flex-col items-center text-center hover:shadow-md transition">
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
        <div className="flex justify-center mt-10 space-x-2">
          {totalPages > 1 && Array.from({ length: totalPages }, (_, i) => (
            <Link
              key={i + 1}
              href={`/products/?page=${i + 1}`}
              className={`px-4 py-2 rounded ${
                currentPage === i + 1 ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-800"
              } hover:bg-blue-500 transition`}
            >
              {i + 1}
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
