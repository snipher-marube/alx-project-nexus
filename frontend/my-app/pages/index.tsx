/* eslint-disable @next/next/no-img-element */
import React, { useState, useEffect } from "react";
import Link from "next/link";
import ImageCarousel from "../components/common/ImageCarousel";
import { ProductList, ProductDetail, CategoryList } from "@/interface/Products";
import CategorySection from '@/components/common/CategorySection';

export async function getServerSideProps() {
  let products: any[] = [];
  let categories: any[] = [];

  let productPage = 1;
  let categoryPage = 1;

  let hasNextProduct = true;
  let hasNextCategory = true;

  try {
    while (hasNextProduct) {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?page=${productPage}`);
      const data = await response.json();

      products.push(...data.results);
      hasNextProduct = !!data.links?.next;
      productPage += 1;
    }

    while (hasNextCategory) {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/categories/?page=${categoryPage}`);
      const data = await response.json();

      categories.push(...data.results);
      hasNextCategory = !!data.links?.next;
      categoryPage += 1;
    }

    // extracting the slugs of each product so i can get the full product detail and extract the category value
    const slugs = products.map((p: any) => p.slug);

    // Fetch product detail by slug
    const detailedResponses = await Promise.all(
      slugs.map(async (slug) => {
        try {
          const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/${slug}/`);
          return await response.json();
        } catch {
          return null;
        }
      })
    );

    // filter products that may return empty..
    const detailedProducts = detailedResponses.filter(Boolean);

    return {
      props: {
        products,
        categories,
        detailedProducts,
      }
    };
  } catch (error) {
    return {
      props: {
        products: [],
        categories: [],
        detailedProducts: [],
      }
    };
  }
}


export default function Home({products, categories, detailedProducts}: {products: ProductList[], categories: CategoryList[], detailedProducts: ProductDetail[]}) {
  const [featured, setFeatured] = useState(products);
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const toggleMenu = (label: string) => {
    setOpenMenu((prev) => (prev === label ? null : label));
  };

  //filtering the roducts based on the featured value
  useEffect(() => {
    const featuredProducts = products.filter((product) => {
      return product.is_featured;
    });
    setFeatured(featuredProducts);
  }, [products]);

  return (
    <main className="text-black min-h-screen bg-neutral-50-100 from-yellow-50 via-white to-stone-100 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-row items-start gap-8">
        {/* Sidebar */}
        <ul className="hidden md:flex flex-col space-y-2 p-4 bg-neutral-50 rounded shadow max-w-sm w-64">
          {categories.map((category) => (
            <li key={category.id}>
              <div
                className="flex items-center justify-between cursor-pointer font-medium hover:text-yellow-500 transition"
                onClick={() => toggleMenu(category.name)}
              >
                <span>{category.name}</span>
                <span className="text-sm ml-2">{openMenu === category.name ? "▼" : "›"}</span>
              </div>
              {openMenu === category.name && (
                <ul className="ml-4 mt-2 pl-2 border-l border-gray-200 space-y-1">
                  {/* {items.map(({ name, href }) => (
                    <li key={name}>
                      <Link
                        href={href}
                        className="block text-sm text-gray-700 hover:text-yellow-500 transition px-1 py-1"
                      >
                        {name}
                      </Link>
                    </li>
                  ))} */}
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
          <h2 className="text-xl font-bold text-gray-800">Featured Products</h2>
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

      {/*displaying products based on categories */}
      <CategorySection
        title="Clothing"
        categoryNames={['Jackets', 'Suits', 'Shirts']}
        products={detailedProducts}
      />

      <CategorySection
        title="Home Appliances"
        categoryNames={['Home Appliances']}
        products={detailedProducts}
      />

      <CategorySection
        title="Health & Beauty"
        categoryNames={['Fragrance', 'Hygeine']}
        products={detailedProducts}
      />

      <CategorySection
        title="Home "
        categoryNames={['Bedding']}
        products={detailedProducts}
      />
    </main>
  );
}
