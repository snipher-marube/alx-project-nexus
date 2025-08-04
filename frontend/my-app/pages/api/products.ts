export default async function handler(req, res) {
  let allResults = [];
  let page = 1;
  let hasNext = true;

  const { search } = req.query;

  try {
    while (hasNext) {
      const queryParam = search ? `search=${encodeURIComponent(search as string)}` : '';
      const response = await fetch(`https://alx-project-nexus-psi.vercel.app/api/v1/products/?${queryParam}&page=${page}`);
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