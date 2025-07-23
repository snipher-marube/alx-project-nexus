import React from "react";
import ImageCarousel from "../components/common/ImageCarousel";

export default function Home() {
  return (
    <main className="text-black min-h-screen bg-gray-100 py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-row items-start gap-8">
        
        {/* Sidebar Menu */}
        <ul className="flex flex-col space-y-5 gap-4 p-4 bg-white rounded shadow max-w-sm w-64">
          {/* Vehicles */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Vehicles
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Cars</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Bikes</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Trucks</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Buses</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Auto-parts</li>
                </ul>
              </div>
            </span>
          </li>

          {/* Electronics */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Electronics
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Mobiles</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Laptops</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">TVs</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Cameras</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Tablets</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Accessories</li>
                </ul>
              </div>
            </span>
          </li>

          {/* Fashion */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Fashion
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Suits</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Shorts</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Shirts</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Dresses</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Skirts</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Shoes</li>
                </ul>
              </div>
            </span>
          </li>

          {/* Home & Furniture */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Home & Furniture
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Beds</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Sofas</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Tables</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Closets</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Cabinets</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Decor</li>
                </ul>
              </div>
            </span>
          </li>

          {/* Health & Beauty */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Health & Beauty
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Makeup</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Skincare</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Supplements</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Hygiene</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Haircare</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Fragrance</li>
                </ul>
              </div>
            </span>
          </li>

          {/* Sports & Fitness */}
          <li className="cursor-pointer">
            <span className="group relative font-medium inline-block">
              Sports & Fitness
              <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 w-max">
                <ul className="grid grid-cols-2 gap-4">
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Gym Equipment</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Activewear</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Footwear</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Yoga Mats</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Supplements</li>
                  <li className="hover:bg-gray-100 px-2 py-1 rounded">Sports Gear</li>
                </ul>
              </div>
            </span>
          </li>
        </ul>

        {/* Image Carousel */}
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
    </main>
  );
}
