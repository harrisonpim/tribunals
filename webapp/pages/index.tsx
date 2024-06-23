import { useEffect, useState } from "react";

import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });


export default function Home() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/health-check")
      .then((response) => response.json())
      .then((jsonData) => setData(jsonData))
      .catch((error) => console.error(error));
  }, []);

  return (
    <main className={`${inter.className} p-8`}>
      <h1 className="text-4xl font-bold">Tribunals search</h1>
      {data !== null && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </main>
  );
}
