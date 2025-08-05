export default async function handler(req, res) {
  const { slug } = req.query;
  let allResults = [];

  try {
    const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/${slug}/`);
    const data = await response.json();

    allResults.push(data);

    res.status(200).json({allResults });
  } catch (error) {
    console.error("API proxy error:", error);
    res.status(500).json({ error: "Proxy failed to fetch products." });
  }
}