/* eslint-disable @next/next/no-img-element */
import React, { useState } from "react";
import Link from "next/link";
import ImageCarousel from "../components/common/ImageCarousel";

const sampleRows = [
  {
    title: "Sponsored products",
    products: [
      { id: "sp-1", name: "NIVEA MEN Deep", price: "KSh 949", image: "/images/products/nivea.jpg" },
      { id: "sp-2", name: "10KG DUMBBELL SET", price: "KSh 2,899", image: "/images/products/dumbbell.jpg" },
      { id: "sp-3", name: "Solar System Kit", price: "KSh 14,700", image: "/images/products/solar.jpg" },
      { id: "sp-4", name: "Ashwagandha Root", price: "KSh 800", image: "/images/products/herbs.jpg" },
    ],
  },
  {
    title: "Top selling items",
    products: [
      { id: "ts-1", name: "MacBook Pro 13\"", price: "KSh 24,500", image: "/images/products/macbook.jpg" },
      { id: "ts-2", name: "Sexy Bra Set", price: "KSh 329", image: "/images/products/bra.jpg" },
      { id: "ts-3", name: "HD 16X Camera", price: "KSh 4,499", image: "/images/products/camera.jpg" },
      { id: "ts-4", name: "Necklace Teardrop", price: "KSh 226", image: "/images/products/necklace.jpg" },
    ],
  },
  {
    title: "Still Your Year | Top Picks For You",
    products: [
      { id: "tp-1", name: "Vitron TV 43\"", price: "KSh 17,255", image: "/images/products/tv.jpg" },
      { id: "tp-2", name: "Electric Kettle", price: "KSh 579", image: "/images/products/kettle.jpg" },
      { id: "tp-3", name: "Twin Tub Washer", price: "KSh 16,999", image: "/images/products/washing.jpg" },
      { id: "tp-4", name: "Refurbished Laptop", price: "KSh 9,999", image: "/images/products/laptop.jpg" },
    ],
  },
];

const menus = [
  {
    label: "Vehicles",
    items: [
      { name: "Cars", href: "/vehicles/cars" },
      { name: "Bikes", href: "/vehicles/bikes" },
      { name: "Trucks", href: "/vehicles/trucks" },
      { name: "Buses", href: "/vehicles/buses" },
      { name: "Auto-parts", href: "/vehicles/auto-parts" },
    ],
  },
  {
    label: "Electronics",
    items: [
      { name: "Mobiles", href: "/electronics/mobiles" },
      { name: "Laptops", href: "/electronics/laptops" },
      { name: "TVs", href: "/electronics/tvs" },
      { name: "Cameras", href: "/electronics/cameras" },
      { name: "Tablets", href: "/electronics/tablets" },
      { name: "Accessories", href: "/electronics/accessories" },
    ],
  },
  {
    label: "Fashion",
    items: [
      { name: "Suits", href: "/fashion/suits" },
      { name: "Shorts", href: "/fashion/shorts" },
      { name: "Shirts", href: "/fashion/shirts" },
      { name: "Dresses", href: "/fashion/dresses" },
      { name: "Skirts", href: "/fashion/skirts" },
      { name: "Shoes", href: "/fashion/shoes" },
    ],
  },
  {
    label: "Home & Furniture",
    items: [
      { name: "Beds", href: "/home/beds" },
      { name: "Sofas", href: "/home/sofas" },
      { name: "Tables", href: "/home/tables" },
      { name: "Closets", href: "/home/closets" },
      { name: "Cabinets", href: "/home/cabinets" },
      { name: "Decor", href: "/home/decor" },
    ],
  },
  {
    label: "Health & Beauty",
    items: [
      { name: "Makeup", href: "/health/makeup" },
      { name: "Skincare", href: "/health/skincare" },
      { name: "Supplements", href: "/health/supplements" },
      { name: "Hygiene", href: "/health/hygiene" },
      { name: "Haircare", href: "/health/haircare" },
      { name: "Fragrance", href: "/health/fragrance" },
    ],
  },
  {
    label: "Sports & Fitness",
    items: [
      { name: "Gym Equipment", href: "/sports/gym-equipment" },
      { name: "Activewear", href: "/sports/activewear" },
      { name: "Footwear", href: "/sports/footwear" },
      { name: "Yoga Mats", href: "/sports/yoga-mats" },
      { name: "Supplements", href: "/sports/supplements" },
      { name: "Sports Gear", href: "/sports/sports-gear" },
    ],
  },
];

export default function Home() {
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const toggleMenu = (label: string) => {
    setOpenMenu((prev) => (prev === label ? null : label));
  };

  return (
    <main className="text-black min-h-screen bg-slate-100 from-yellow-50 via-white to-stone-100 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-row items-start gap-8">
        {/* Sidebar */}
        <ul className="hidden md:flex flex-col space-y-2 p-4 bg-white rounded shadow max-w-sm w-64">
          {menus.map(({ label, items }) => (
            <li key={label}>
              <div
                className="flex items-center justify-between cursor-pointer font-medium hover:text-yellow-500 transition"
                onClick={() => toggleMenu(label)}
              >
                <span>{label}</span>
                <span className="text-sm ml-2">{openMenu === label ? "▼" : "›"}</span>
              </div>
              {openMenu === label && (
                <ul className="ml-4 mt-2 pl-2 border-l border-gray-200 space-y-1">
                  {items.map(({ name, href }) => (
                    <li key={name}>
                      <Link
                        href={href}
                        className="block text-sm text-gray-700 hover:text-yellow-500 transition px-1 py-1"
                      >
                        {name}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>

        {/* Carousel */}
        <div className="flex-1">
          <ImageCarousel
            images={[
              "/images/carousel1.jpg",
              "/images/carousel2.jpg",
              "/images/carousel3.jpg",
              "/images/carousel4.jpg",
            ]}
          />
        </div>
      </div>

      {/* Dynamic Rows Below Carousel */}
      <div className="max-w-7xl mx-auto mt-12 space-y-12">
        {sampleRows.map((section) => (
          <div key={section.title}>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xl font-bold text-gray-800">{section.title}</h2>
              <a href="#" className="text-blue-600 hover:underline text-sm">
                See All
              </a>
            </div>
            <div className="overflow-x-auto">
              <div className="flex space-x-6">
                {section.products.map((product, i) => (
                  <Link
                    key={i}
                    href={`/products/${product.id}`}
                    className="min-w-[220px] bg-white rounded-lg shadow p-4 hover:shadow-md transition"
                  >
                    <div>
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-36 object-cover mb-2 rounded"
                      />
                      <p className="text-sm font-medium text-gray-800">{product.name}</p>
                      <p className="text-green-600 font-bold">{product.price}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
