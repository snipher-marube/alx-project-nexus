/* eslint-disable @next/next/no-img-element */
import { GetServerSideProps } from "next";
import { Product } from "@/interface/Products";
import { useCart } from "@/context/CartContext";

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { slug } = context.params!;
  try {
    const res = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/${slug}`);
    if (!res.ok) throw new Error("Product not found");
    const product = await res.json();

    if (!product || !product.id || !product.name) {
      throw new Error("Invalid product data");
    }

    return {
      props: { product },
    };  
  } catch (error) {
    return {
      props: { product: null },
    };
  }
};



export default function ProductDetailPage( {product}: {product: Product}) {
  const { addToCart } = useCart();

  return (
    <main className="p-6 bg-gray-100 min-h-screen text-black">
      <div className="max-w-4xl mx-auto bg-neutral-50 rounded shadow-md p-6 flex flex-col md:flex-row gap-8">
        <img
          src={product.primary_image.image_url}
          alt={product.primary_image.image_url}
          className="w-full md:w-1/2 h-80 object-cover rounded"
        />
        <div className="flex-1">
          <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
          <p className="text-green-600 font-bold text-xl mb-4">${product.price}</p>
          <p className="text-gray-700 mb-6">{product.description}</p>
          <button
            className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
            onClick={() => {
              addToCart(product);
              alert("Added to cart!");
            }}
          >
            Add to Cart
          </button>
        </div>
      </div>
    </main>
  );
}

