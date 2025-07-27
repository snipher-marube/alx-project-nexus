/* eslint-disable @next/next/no-img-element */

import Link from "next/link";

const sampleProducts = [
  {
    id: "e-m-1",
    title: "iPhone 14 Pro",
    price: "KSh 180,000",
    image: "/images/products/iphone.jpg",
  },
  {
    id: "f-s-3",
    title: "Unisex Sneakers",
    price: "KSh 6,000",
    image: "/images/products/sneakers.jpg",
  },
  {
    id: "h-b-2",
    title: "6x6 King Bed",
    price: "KSh 40,000",
    image: "/images/products/bed2.jpg",
  },
  {
    id: "e-m-2",
    title: "Samsung Galaxy S23",
    price: "KSh 150,000",
    image: "/images/products/samsung.jpg",
  },
  {
    id: "f-s-4",
    title: "Leather Jacket",
    price: "KSh 8,500",
    image: "/images/products/jacket.jpg",
  },
  {
    id: "h-b-3",
    title: "Wooden Dining Table",
    price: "KSh 25,000",
    image: "/images/products/dining.jpg",
  },
];

export default function ProductGrid() {
  return (
    <section className="mt-12">
      <h2 className="text-2xl font-bold mb-6">Featured Products</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {sampleProducts.map((product) => (
          <Link
            key={product.id}
            href={`/products/${product.id}`}
            className="block bg-white rounded shadow p-4 hover:shadow-lg transition"
          >
            <img
              src={product.image}
              alt={product.title}
              className="w-full h-40 object-cover rounded mb-3"
            />
            <h3 className="text-lg font-semibold">{product.title}</h3>
            <p className="text-green-600 font-bold">{product.price}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
