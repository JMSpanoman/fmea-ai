import React, { useState, useEffect } from "react";

interface Capa {
  id: string;
  issueDescription: string;
  source: string;
  detectionDate: string;
  severity: string;
  rootCause: string;
  correctiveAction: string;
  preventiveAction: string;
  actionOwner: string;
  dueDate: string;
  status: string;
  effectivenessCheckPlan: string;
  fmeaLink: string;
  regulatoryImpact: string;
  closureSummary: string;
  milestones: string;
  riskControlsUpdate: string;
}

interface CapaFormProps {
  onSubmit: (capa: Capa) => void;
  prefillIssueDescription?: string;
}

const CapaForm: React.FC<CapaFormProps> = ({ onSubmit, prefillIssueDescription }) => {
  const [form, setForm] = useState({
    issueDescription: prefillIssueDescription || "",
    source: "",
    detectionDate: "",
    severity: "",
    rootCause: "",
    correctiveAction: "",
    preventiveAction: "",
    actionOwner: "",
    dueDate: "",
    effectivenessCheckPlan: "",
    fmeaLink: "",
    regulatoryImpact: "",
    closureSummary: "",
    milestones: "",
    riskControlsUpdate: "",
  });

  useEffect(() => {
    setForm((prev) => ({ ...prev, issueDescription: prefillIssueDescription || "" }));
  }, [prefillIssueDescription]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newCapa: Capa = {
      ...form,
      id: Date.now().toString(),
      status: "Open"
    };
    onSubmit(newCapa);
    setForm({
      issueDescription: prefillIssueDescription || "",
      source: "",
      detectionDate: "",
      severity: "",
      rootCause: "",
      correctiveAction: "",
      preventiveAction: "",
      actionOwner: "",
      dueDate: "",
      effectivenessCheckPlan: "",
      fmeaLink: "",
      regulatoryImpact: "",
      closureSummary: "",
      milestones: "",
      riskControlsUpdate: "",
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-2xl shadow-md max-w-4xl mx-auto mb-6">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Create New CAPA</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Issue Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Issue Description *</label>
          <textarea 
            name="issueDescription" 
            placeholder="Describe the issue, nonconformity, or problem that requires corrective and preventive action..." 
            value={form.issueDescription} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={4}
            required 
          />
        </div>

        {/* Source */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Source *</label>
          <input 
            name="source" 
            placeholder="e.g., Complaint, NC, Audit, Customer Feedback" 
            value={form.source} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            required 
          />
        </div>

        {/* Detection Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Detection Date *</label>
          <input 
            type="date" 
            name="detectionDate" 
            value={form.detectionDate} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            required 
          />
        </div>

        {/* Severity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Severity *</label>
          <select 
            name="severity" 
            value={form.severity} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            required
          >
            <option value="">Select Severity</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        {/* Root Cause */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Root Cause Analysis *</label>
          <textarea 
            name="rootCause" 
            placeholder="Describe the root cause analysis and findings..." 
            value={form.rootCause} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={3}
            required 
          />
        </div>

        {/* Corrective Actions */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Corrective Actions *</label>
          <textarea 
            name="correctiveAction" 
            placeholder="Steps to eliminate the cause of the existing nonconformity..." 
            value={form.correctiveAction} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={4}
            required 
          />
        </div>

        {/* Preventive Actions */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Preventive Actions</label>
          <textarea 
            name="preventiveAction" 
            placeholder="Steps to prevent future recurrence, even in related processes/products..." 
            value={form.preventiveAction} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={4}
          />
        </div>

        {/* Action Owner */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Action Owner(s) *</label>
          <input 
            name="actionOwner" 
            placeholder="e.g., Dr. Sarah Chen, Engineering Team" 
            value={form.actionOwner} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            required 
          />
        </div>

        {/* Due Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Due Date *</label>
          <input 
            type="date" 
            name="dueDate" 
            value={form.dueDate} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            required 
          />
        </div>

        {/* Milestones */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Due Dates and Milestones</label>
          <textarea 
            name="milestones" 
            placeholder="Key milestones and their target dates..." 
            value={form.milestones} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={3}
          />
        </div>

        {/* Effectiveness Check Plan */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Effectiveness Check Plan</label>
          <textarea 
            name="effectivenessCheckPlan" 
            placeholder="How and when you'll verify the CAPA worked..." 
            value={form.effectivenessCheckPlan} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={3}
          />
        </div>

        {/* FMEA Link */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Link to FMEA</label>
          <input 
            name="fmeaLink" 
            placeholder="e.g., FMEA-51, Risk Control-23" 
            value={form.fmeaLink} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
          />
        </div>

        {/* Risk Controls Update */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Risk Controls Update</label>
          <input 
            name="riskControlsUpdate" 
            placeholder="Traceability to design updates, risk documentation" 
            value={form.riskControlsUpdate} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
          />
        </div>

        {/* Regulatory Impact */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Regulatory Impact</label>
          <textarea 
            name="regulatoryImpact" 
            placeholder="Any filings (e.g., MDR, FDA reporting) triggered? Regulatory implications..." 
            value={form.regulatoryImpact} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={3}
          />
        </div>

        {/* Closure Summary */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Closure Summary</label>
          <textarea 
            name="closureSummary" 
            placeholder="Verification results, sign-off by QA, etc..." 
            value={form.closureSummary} 
            onChange={handleChange} 
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
            rows={3}
          />
        </div>
      </div>

      <div className="flex space-x-4 pt-4">
        <button 
          type="submit" 
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
        >
          Submit CAPA
        </button>
        <button 
          type="button" 
          onClick={() => window.history.back()} 
          className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default CapaForm; 