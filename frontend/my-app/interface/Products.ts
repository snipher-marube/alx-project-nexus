//api products response interface
export interface ProductsResponse {
  links: {
    next: string | null;
    previous: string | null;
  }
  count: number;
  page_size: number;
  results: ProductList[];
}

//each product returned interface and saved as an array in the result value of the api response..
export interface ProductList {
  id: number;
  name: string;
  slug: string;
  price: string;
  primary_image: {
    image_url: string;
    alt_text: string;
  };
  category: {
    name: string;
  };
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
  primary_image: {
    image_url: string;
    alt_text: string;
  };
  description: string;
  quantity: number;
  is_featured: boolean;
}