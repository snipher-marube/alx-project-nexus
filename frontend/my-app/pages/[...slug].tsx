/* eslint-disable @next/next/no-img-element */

import { useRouter } from "next/router";
import Link from "next/link";

const allProducts = [
  // Electronics - Mobiles
  { id: "e-m-1", title: "iPhone 14 Pro", category: "electronics", subcategory: "mobiles", price: "KSh 180,000", image: "/images/products/iphone.jpg" },
  { id: "e-m-2", title: "Samsung Galaxy S22", category: "electronics", subcategory: "mobiles", price: "KSh 120,000", image: "/images/products/galaxy.jpg" },
  { id: "e-m-3", title: "Infinix Hot 12", category: "electronics", subcategory: "mobiles", price: "KSh 18,000", image: "/images/products/infinix.jpg" },
  { id: "e-m-4", title: "Tecno Spark 10", category: "electronics", subcategory: "mobiles", price: "KSh 16,500", image: "/images/products/tecno.jpg" },
  { id: "e-m-5", title: "Xiaomi Redmi Note 12", category: "electronics", subcategory: "mobiles", price: "KSh 22,000", image: "/images/products/redmi.jpg" },

  // Fashion - Shoes
  { id: "f-s-1", title: "Men's Running Shoes", category: "fashion", subcategory: "shoes", price: "KSh 4,500", image: "/images/products/shoes1.jpg" },
  { id: "f-s-2", title: "Women's Heels", category: "fashion", subcategory: "shoes", price: "KSh 3,800", image: "/images/products/heels.jpg" },
  { id: "f-s-3", title: "Unisex Sneakers", category: "fashion", subcategory: "shoes", price: "KSh 6,000", image: "/images/products/sneakers.jpg" },
  { id: "f-s-4", title: "Kid's Sports Shoes", category: "fashion", subcategory: "shoes", price: "KSh 2,000", image: "/images/products/kids-shoes.jpg" },
  { id: "f-s-5", title: "Formal Office Shoes", category: "fashion", subcategory: "shoes", price: "KSh 5,200", image: "/images/products/formal.jpg" },

  // Home - Beds
  { id: "h-b-1", title: "5x6 Wooden Bed", category: "home", subcategory: "beds", price: "KSh 28,000", image: "/images/products/bed1.jpg" },
  { id: "h-b-2", title: "6x6 King Bed", category: "home", subcategory: "beds", price: "KSh 40,000", image: "/images/products/bed2.jpg" },
  { id: "h-b-3", title: "Metal Bunk Bed", category: "home", subcategory: "beds", price: "KSh 18,000", image: "/images/products/bunk.jpg" },
  { id: "h-b-4", title: "Upholstered Bed Frame", category: "home", subcategory: "beds", price: "KSh 35,000", image: "/images/products/upholstered.jpg" },
  { id: "h-b-5", title: "Kids Bed With Storage", category: "home", subcategory: "beds", price: "KSh 25,000", image: "/images/products/kids-bed.jpg" },
];

export default function CategoryPage() {
  const router = useRouter();
  const { slug } = router.query;
  const [category, subcategory] = Array.isArray(slug) ? slug : [];

  const filtered = allProducts.filter(
    (p) => p.category === category && p.subcategory === subcategory
  );

  return (
    <main className="p-6 bg-gray-100 min-h-screen text-black">
      <h1 className="text-2xl font-bold mb-6 capitalize">
        {subcategory ? `${subcategory} in ${category}` : "Category"}
      </h1>

      {filtered.length === 0 ? (
        <p className="text-gray-600">No products found in this category.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {filtered.map((p) => (
            <Link href={`/products/${p.id}`} key={p.id}>
              <div className="bg-white rounded shadow p-4 hover:shadow-lg cursor-pointer">
                <img
                  src={p.image}
                  alt={p.title}
                  className="w-full h-40 object-cover rounded mb-3"
                />
                <h2 className="text-lg font-semibold mb-1">{p.title}</h2>
                <p className="text-green-600 font-bold mb-2">{p.price}</p>
                <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                  Add to Cart
                </button>
              </div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
