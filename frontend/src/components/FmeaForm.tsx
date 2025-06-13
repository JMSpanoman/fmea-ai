import React, { useState } from 'react';

interface FmeaFormProps {
  onSubmit: (formData: {
    component: string;
    failureMode: string;
    effect: string;
    cause: string;
  }) => void;
}

const FmeaForm: React.FC<FmeaFormProps> = ({ onSubmit }) => {
  const [component, setComponent] = useState('');
  const [failureMode, setFailureMode] = useState('');
  const [effect, setEffect] = useState('');
  const [cause, setCause] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ component, failureMode, effect, cause });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-2xl shadow-md">
      <div>
        <label className="block text-sm font-medium text-gray-700">Component</label>
        <input
          type="text"
          value={component}
          onChange={(e) => setComponent(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Failure Mode</label>
        <input
          type="text"
          value={failureMode}
          onChange={(e) => setFailureMode(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Effect</label>
        <input
          type="text"
          value={effect}
          onChange={(e) => setEffect(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Cause</label>
        <input
          type="text"
          value={cause}
          onChange={(e) => setCause(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
        />
      </div>
      <button
        type="submit"
        className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 shadow"
      >
        Generate FMEA
      </button>
    </form>
  );
};

export default FmeaForm;
