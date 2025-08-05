{/*
	const fetchProductsByCategory = async (category: string) => {
    let matchingSlugs: string[] = [];
    let page = 1;
    let hasNext = true;

    try {
      while(hasNext) {
        const res = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?search=${encodeURIComponent(category)}&page=${page}`);
        const data = await res.json();

        const products = data.results;

        const slugs = products.map((p: any) => p.slug);
        matchingSlugs.push(...slugs);
        hasNext = !!data.links?.next;
        page++;
      }
    }catch (error) {
      console.error("Error fetching product list:", error);
      return [];
    }

    const productDetails = await Promise.all(
      matchingSlugs.map(async (slug) => {
        try {
          const res = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/${slug}`);
          if (!res.ok) throw new Error(`Failed to fetch slug: ${slug}`);
          return await res.json();
        }catch (error) {
					console.warn(`Skipping slug ${slug} due to error.`);
					return null;
        };
			})
    );

		const validProducts = productDetails.filter((item) => item !== null);
		console.log(validProducts);
  	return validProducts;
  }
*/}

// /api/products-by-category.ts
export default async function handler(req, res) {
  //const { category } = req.query;
  let allResults = [];
  let page = 1;
  let hasNext = true;

  try {
    while (hasNext) {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?page=${page}`);
      const data = await response.json();

      allResults.push(...data.results);
      hasNext = !!data.links?.next;
      page += 1;
    }

    res.status(200).json({ results: allResults });
  } catch (error) {
    console.error("API proxy error:", error);
    res.status(500).json({ error: "Proxy failed to fetch products." });
  }
}