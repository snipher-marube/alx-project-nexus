export default async function handler(req, res) {
  try {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?category=${category_slug}`);
      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
    res.status(500).json({ error: "Failed to fetch products." });
  }
}