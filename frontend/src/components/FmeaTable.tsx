import React from 'react';

interface FmeaRow {
  id: number;
  component: string;
  failureMode: string;
  effect: string;
  cause: string;
  severity: number;
  probability: number;
  detection: number;
  rpn: number;
  mitigation: string;
  actionTaken: string;
  revisedSeverity: number;
  revisedProbability: number;
  revisedDetection: number;
  revisedRpn: number;
}

interface FmeaTableProps {
  data: FmeaRow[];
}

const FmeaTable: React.FC<FmeaTableProps> = ({ data }) => {
  return (
    <div className="overflow-x-auto rounded-2xl shadow-md bg-white p-4">
      <table className="min-w-full table-auto text-sm text-left text-gray-700">
        <thead className="bg-gray-100 text-xs uppercase text-gray-600">
          <tr>
            <th className="px-3 py-2">ID</th>
            <th className="px-3 py-2">Component</th>
            <th className="px-3 py-2">Failure Mode</th>
            <th className="px-3 py-2">Effect</th>
            <th className="px-3 py-2">Cause</th>
            <th className="px-3 py-2">Severity</th>
            <th className="px-3 py-2">Probability</th>
            <th className="px-3 py-2">Detection</th>
            <th className="px-3 py-2">RPN</th>
            <th className="px-3 py-2">Mitigation</th>
            <th className="px-3 py-2">Action Taken</th>
            <th className="px-3 py-2">Rev. Sev.</th>
            <th className="px-3 py-2">Rev. Prob.</th>
            <th className="px-3 py-2">Rev. Det.</th>
            <th className="px-3 py-2">Rev. RPN</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id} className="border-t border-gray-200 hover:bg-gray-50">
              <td className="px-3 py-2">{row.id}</td>
              <td className="px-3 py-2">{row.component}</td>
              <td className="px-3 py-2">{row.failureMode}</td>
              <td className="px-3 py-2">{row.effect}</td>
              <td className="px-3 py-2">{row.cause}</td>
              <td className="px-3 py-2 text-center">{row.severity}</td>
              <td className="px-3 py-2 text-center">{row.probability}</td>
              <td className="px-3 py-2 text-center">{row.detection}</td>
              <td className="px-3 py-2 text-center font-semibold">{row.rpn}</td>
              <td className="px-3 py-2">{row.mitigation}</td>
              <td className="px-3 py-2">{row.actionTaken}</td>
              <td className="px-3 py-2 text-center">{row.revisedSeverity}</td>
              <td className="px-3 py-2 text-center">{row.revisedProbability}</td>
              <td className="px-3 py-2 text-center">{row.revisedDetection}</td>
              <td className="px-3 py-2 text-center font-semibold">{row.revisedRpn}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FmeaTable;