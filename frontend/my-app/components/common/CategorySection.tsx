// components/CategorySection.tsx
import Link from 'next/link';

interface Product {
  id: number;
  name: string;
  slug: string;
  price: number;
  category: { name: string };
  primary_image?: { image_url: string };
}

interface Props {
  title: string;
  categoryNames: string[];
  products: Product[];
}

export default function CategorySection({ title, categoryNames, products }: Props) {
  const filteredProducts = products.filter((product) =>
    categoryNames.includes(product.category?.name)
  );

  if (filteredProducts.length === 0) return null;

  return (
    <div className="max-w-7xl mx-auto mt-12 space-y-12">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-bold text-gray-800">{title}</h2>
        <Link href="/products" className="text-blue-600 hover:underline text-sm">
          See All
        </Link>
      </div>
      <div className="flex flex-col md:flex-row gap-4 overflow-x-auto py-5">
        {filteredProducts.map((product) => (
          <div key={product.id} className="flex space-x-6">
            <Link
              href={`/products/${product.slug}`}
              className="min-w-[220px] bg-neutral-50 rounded-lg shadow p-4 hover:shadow-md transition"
            >
              <img
                src={product.primary_image?.image_url}
                alt={product.name}
                className="w-full h-36 object-cover mb-2 rounded"
              />
              <p className="text-sm font-medium text-gray-800">{product.name}</p>
              <p className="text-green-600 font-bold">${product.price}</p>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}