
import Layout from "@/components/layout/Layout";
import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { OrderProvider } from "@/context/OrderContext";
import { CartProvider } from "@/context/CartContext";
import { AuthProvider } from "@/context/AuthContext";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>  
      <OrderProvider>
        <CartProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </CartProvider>
      </OrderProvider>
    </AuthProvider>
  );
}
