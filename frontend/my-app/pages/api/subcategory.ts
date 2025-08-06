export default async function handler(req, res) {
  let allResults = [];
  try {
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/categories/`);
      const data = await response.json();

      allResults.push(...data.results);

    res.status(200).json({ results: allResults });
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch products." });
  }
}