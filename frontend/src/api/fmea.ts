export async function getFmeas() {
  const res = await fetch("http://localhost:8000/fmea/");
  return res.json();
}

export async function createFmea(data: any) {
  const res = await fetch("http://localhost:8000/fmea/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}
