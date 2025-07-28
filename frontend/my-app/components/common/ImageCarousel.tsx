'use client'
import { useState, useEffect } from "react";

const images = [
  "/assets/carousel/img-1.gif",
  "/assets/carousel/img-2.gif",
  "/assets/carousel/img-3.gif",
  "/assets/carousel/img-4.jpg",
  "/assets/carousel/img-5.gif",
];

export default function ImageCarousel() {
  const [current, setCurrent] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const total = images.length;

  const prevSlide = () => {
    setCurrent((prev) => (prev === 0 ? total - 1 : prev - 1));
  };

  const nextSlide = () => {
    setCurrent((prev) => (prev === total - 1 ? 0 : prev + 1));
  };

  useEffect(() => {
    if (isHovered) return;

    const interval = setInterval(() => {
      setCurrent((prev) => (prev === total - 1 ? 0 : prev + 1));
    }, 3000);

    return () => clearInterval(interval);
  }, [isHovered, total]);

  return (
    <div
      className="relative w-full overflow-hidden rounded-lg shadow-lg"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className="flex transition-transform duration-700 ease-in-out"
        style={{ transform: `translateX(-${current * 100}%)` }}
      >
        {images.map((src, index) => (
          <div
            key={index}
            className="min-w-full h-[500px] md:h-[500px] relative"
          >
            <img
              src={src}
              alt={`Slide ${index + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>

      <button
        onClick={prevSlide}
        aria-label="Previous slide"
        className="absolute top-1/2 left-4 transform -translate-y-1/2 bg-opacity-50 hover:bg-opacity-80 text-black p-2 rounded-full"
      >
        &#10094;
      </button>
      <button
        onClick={nextSlide}
        aria-label="Next slide"
        className="absolute top-1/2 right-4 transform -translate-y-1/2 bg-opacity-50 hover:bg-opacity-80 text-red-500 p-2 rounded-full"
      >
        &#10095;
      </button>
    </div>
  );
}
