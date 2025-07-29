/* eslint-disable @next/next/no-img-element */
import React from "react";

interface ProductProps {
  image: string;
  name: string;
  price: number;
  oldPrice?: number;
  discountPercent?: number;
  onAddToCart?: () => void;
}

const ProductCard: React.FC<ProductProps> = ({
  image,
  name,
  price,
  oldPrice,
  discountPercent,
  onAddToCart,
}) => {
  return (
    <div className="relative bg-white rounded shadow-md overflow-hidden w-60 hover:shadow-lg transition">
      {/* Discount Label */}
      {discountPercent && (
        <div className="absolute top-0 right-0 bg-orange-100 text-orange-600 text-xs px-2 py-1 rounded-bl">
          –{discountPercent}%
        </div>
      )}

      {/* Product Image */}
      <img src={image} alt={name} className="w-full h-48 object-cover" />

      {/* Product Info */}
      <div className="p-3 space-y-1">
        <p className="text-sm text-gray-800 truncate">{name}</p>
        <p className="text-lg font-semibold text-black">KSh {price.toLocaleString()}</p>
        {oldPrice && (
          <p className="text-sm text-gray-500 line-through">KSh {oldPrice.toLocaleString()}</p>
        )}
      </div>

      {/* Add to Cart Button */}
      <div className="p-3 pt-0">
        <button
          onClick={onAddToCart}
          className="w-full text-sm bg-yellow-400 hover:bg-yellow-500 text-white font-medium py-2 rounded transition"
        >
          🛒 Add to Cart
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
