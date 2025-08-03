import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface CartItem {
  id: number;
  name: string;
  primary_image: {
    image_url: string;
    alt_text: string;
  };
  price: number;
  quantity: number;
}

interface CartContextType {
  cart: CartItem[];
  addToCart: (item: any) => void; 
  removeFromCart: (id: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const [cart, setCart] = useState<CartItem[]>([]);

  
  useEffect(() => {
    const storedCart = localStorage.getItem("cart");
    if (storedCart) {
      setCart(JSON.parse(storedCart));
    }
  }, []);

  
  useEffect(() => {
    if (cart.length > 0) {
      localStorage.setItem("cart", JSON.stringify(cart));
    } else {
      localStorage.removeItem("cart");
    }
  }, [cart]);

  const addToCart = (item: any) => {
    setCart((prev) => {
      const exists = prev.find((i) => i.id === item.id);
      if (exists) {
        return prev.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      
      
      const priceAsNumber = parseFloat(item.price.replace(/[^\d.]/g, ""));

      return [...prev, { 
          ...item, 
          price: priceAsNumber,
          quantity: 1 
      }];
    });
  };

  const removeFromCart = (id: number) => {
    setCart((prev) => prev.filter((i) => i.id !== id));
  };

  const clearCart = () => {
    setCart([]);
  };

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, clearCart }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};