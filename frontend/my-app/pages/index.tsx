/* eslint-disable @next/next/no-img-element */
import React, { useState, useEffect } from "react";
import Link from "next/link";
import ImageCarousel from "../components/common/ImageCarousel";
import { ProductList, ProductsResponse } from "@/interface/Products";


export async function getServerSideProps() {
  let products = [];
  let page = 1;
  let hasNext = true;

  try {
    while (hasNext) {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?page=${page}`);
      const data = await response.json();

      products.push(...data.results);
      hasNext = !!data.links?.next;
      page += 1;
    }
    //res.status(200).json({ results: products });
    return {
      props: {
        products,
      }
    }
  } catch (error) {
    //res.status(500).json({ error: "Failed to fetch products." });
    return {
      props: {
        products: [],
      }
    }
  }
}


export default function Home({products, fashionProducts }: {products: ProductList[], fashionProducts: ProductList[]}) {
  const [featured, setFeatured] = useState(products);
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const toggleMenu = (label: string) => {
    setOpenMenu((prev) => (prev === label ? null : label));
  };

  
  useEffect(() => {
    const featuredProducts = products.filter((product) => {
      return product.is_featured;
    });
    setFeatured(featuredProducts);
  }, [products]);

  //console.log(featured);
  //console.log(fashionProducts);

  const menus = [
  
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
        { name: "Shorts", href: "/fashion/Jackets" },
        { name: "Shirts", href: "/fashion/shirts" },
        { name: "Shoes", href: "/fashion/shoes" },
      ],
    },
    {
      label: "Home & Office",
      items: [
        { name: "Furniture", href: "/home/beds" },
        { name: "Bedding", href: "/home/sofas" },
        { name: "Kitchen", href: "/home/tables" },
        { name: "Appliances", href: "/home/closets" },
      ],
    },
    {
      label: "Health & Beauty",
      items: [
        { name: "Makeup", href: "/health/makeup" },
        { name: "Hygiene", href: "/health/hygiene" },
        { name: "Haircare", href: "/health/haircare" },
        { name: "Fragrance", href: "/health/fragrance" },
      ],
    },
  ];

    return (
    <main className="text-black min-h-screen bg-neutral-50-100 from-yellow-50 via-white to-stone-100 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-row items-start gap-8">
        {/* Sidebar */}
        <ul className="hidden md:flex flex-col space-y-2 p-4 bg-neutral-50 rounded shadow max-w-sm w-64">
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
              "../public/assets/carousel/img-1.gif",
              "../public/assets/carousel/img-2.gif",
              "../public/assets/carousel/img-3.gif",
              "../public/assets/carousel/img-4.jpg",
              "../public/assets/carousel/img-5.gif",
            ]}
          />
        </div>
      </div>

      {/* featured Products section */}
      <div className="max-w-7xl mx-auto mt-12 space-y-12">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gray-800">Featured Products {featured.length}</h2>
          <Link href="/products" className="text-blue-600 hover:underline text-sm">
            See All
          </Link>
        </div>
        <div className="flex flex-col md:flex-row gap-4 overflow-x-auto py-5">
          {featured.map((product) => (
            <div className="" key={product.id}>
              <div className="flex space-x-6">
                <Link
                  
                  href={`/products/${product.slug}`}
                  className="min-w-[220px] bg-neutral-50 rounded-lg shadow p-4 hover:shadow-md transition"
                >
                  <div>
                    <img
                      src={product.primary_image.image_url}
                      alt={product.name}
                      className="w-full h-36 object-cover mb-2 rounded"
                    />
                    <p className="text-sm font-medium text-gray-800">{product.name}</p>
                    <p className="text-green-600 font-bold">{product.price}</p>
                  </div>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
{/*}
      <div className="max-w-7xl mx-auto mt-12 space-y-12">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gray-800">Fashion {fashionProducts.length}</h2>
          <Link href="/products" className="text-blue-600 hover:underline text-sm">
            See All
          </Link>
        </div>
        <div className="flex flex-col md:flex-row gap-4 overflow-x-auto py-5">
          {fashionProducts.map((product) => (
            <div className="">
              <div className="flex space-x-6">
                <Link
                  key={product.id}
                  href={`/products/${product.slug}`}
                  className="min-w-[220px] bg-neutral-50 rounded-lg shadow p-4 hover:shadow-md transition"
                >
                  <div>
                    <img
                      src={product.primary_image.image_url}
                      alt={product.name}
                      className="w-full h-36 object-cover mb-2 rounded"
                    />
                    <p className="text-sm font-medium text-gray-800">{product.name}</p>
                    <p className="text-green-600 font-bold">{product.price}</p>
                  </div>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
*/}
    </main>
  );
}
