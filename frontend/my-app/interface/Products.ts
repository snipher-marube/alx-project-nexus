export interface ProductsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ProductList[];
}


export interface ProductList {
  id: number;
  name: string;
  slug: string;
  price: string;
  primary_image: string;
  quantity: number;
  compare_at_price?: string;
  discount_percentage?: string;
  average_rating?: number;
  inventory_status?: string;
  is_featured?: boolean;
  created_at?: string;
}


//each product interface
export interface Product {
  id: number;
  name: string;
  slug: string;
  price: string;
  primary_image: string;
  description: string;
  quantity: number;
}