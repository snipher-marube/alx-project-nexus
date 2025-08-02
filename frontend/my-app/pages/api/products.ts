export default async function handler(req, res) {
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
    res.status(500).json({ error: "Failed to fetch products." });
  }
}