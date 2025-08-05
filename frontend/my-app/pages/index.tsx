/* eslint-disable @next/next/no-img-element */
import React, { useState, useEffect } from "react";
import Link from "next/link";
import ImageCarousel from "../components/common/ImageCarousel";
import { ProductList, ProductDetail } from "@/interface/Products";
import CategorySection from '@/components/common/CategorySection';

interface CategoryList {
  id: number;
  name: string;
  slug: string;
  full_path: string;
}

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


export default function Home({products}: {products: ProductList[]}) {
  const [featured, setFeatured] = useState(products);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [categories, setCategories] = useState<CategoryList[]>([]);

  const [productsList, setProductsList] = useState([]); //all products fetched
  const [productSlug, setProductSlug] = useState<string[]>([]); //extracted all products slugs
  const [detailedProducts, setDetailedProducts] = useState<ProductDetail[]>([]); //saved the details of each product
  //i did the above steps so i can extract the category value from each product so i can use it to display some products
  //based on their category..

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

  //fetching the categories so i can display the categories menu..
  useEffect(() => {
    const CategoryList = async () => {
      try {
        const res = await fetch('/api/category');
        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status}`);
        }
        const data = await res.json();

        console.log('Fetched category data:', data);

        const category: CategoryList[] = data.results;

        setCategories(category);
      } catch(error) {
        console.log('error fetching categories', error)
      }
    };
    CategoryList();
  }, []);


//fetching all the products so i can extract their slugs..
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const res = await fetch(`/api/product`);
        const data = await res.json();

        const products = data.results;
        setProductsList(products);
      } catch (error) {
        console.error('Error loading category products:', error);
      }
    };
    loadProducts();
  }, []);

  //extracting the slugs into an array so i can map thru them..
  useEffect(() => {
    if (Array.isArray(productsList) && productsList.length > 0) {
      const allSlugs: string[] = productsList.map((p: any) => p.slug);
      setProductSlug(allSlugs);
    }
  }, [productsList]);

  //fetch each product so i can get the category value..
  useEffect(() => {
    const fetchProductDetails = async () => {
      try {
        const responses: ProductDetail[] = await Promise.all(
          productSlug.map(async (slug) => {
            const res = await fetch(`/api/product-slug?slug=${encodeURIComponent(slug)}`);
            if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
            const data = await res.json();
            return data.allResults;
          })
        );

        setDetailedProducts(responses);
      } catch (error) {
        console.error('Error loading product details:', error);
      }
    };
    if (productSlug.length > 0) {
      fetchProductDetails();
    }
  }, [productSlug]);

  //the array was nested so i have to flatten it..
  const flattenedProducts = detailedProducts.flat();

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

      {/*home appliances */}
      <CategorySection
        title="Clothing"
        categoryNames={['Jackets', 'Suits', 'Shirts']}
        products={flattenedProducts}
      />

      <CategorySection
        title="Home Appliances"
        categoryNames={['Home Appliances']}
        products={flattenedProducts}
      />

      <CategorySection
        title="Health & Beauty"
        categoryNames={['Fragrance', 'Hygeine']}
        products={flattenedProducts}
      />

      <CategorySection
        title="Home "
        categoryNames={['Bedding']}
        products={flattenedProducts}
      />



    </main>
  );
}
