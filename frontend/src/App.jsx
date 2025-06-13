import React, { useState } from "react";
import FmeaForm from "./components/FmeaForm";
import FmeaTable from "./components/FmeaTable";

function App() {
  const [fmeaRows, setFmeaRows] = useState([]);

  const handleFormSubmit = async (formData: any) => {
    try {
      const response = await fetch("https://your-backend-url/api/fmea", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setFmeaRows((prevRows) => [...prevRows, ...data]);
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <div className="min-h-screen bg-white p-4">
      <h1 className="text-3xl font-bold mb-4 text-center">Smart FMEA Builder</h1>
      <FmeaForm onSubmit={handleFormSubmit} />
      <FmeaTable data={fmeaRows} />
    </div>
  );
}

export default App;
