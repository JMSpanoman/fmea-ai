import React, { useState } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { generateDesignOutputs, DesignOutputItem } from '../services/apiService';

interface GenerateDesignOutputsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDesignOutputsGenerated?: (designOutputs: DesignOutputItem[]) => void;
}

const GenerateDesignOutputsModal: React.FC<GenerateDesignOutputsModalProps> = ({
  isOpen,
  onClose,
  onDesignOutputsGenerated,
}) => {
  const [componentName, setComponentName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedOutputs, setGeneratedOutputs] = useState<DesignOutputItem[]>([]);

  const handleGenerate = async () => {
    if (!componentName.trim()) {
      setError('Please enter a component name');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedOutputs([]);

    try {
      // Call AI API to generate design outputs using the apiService (similar to Design Inputs)
      const data = await generateDesignOutputs(componentName.trim(), 5);
      
      if (data.design_outputs && Array.isArray(data.design_outputs)) {
        setGeneratedOutputs(data.design_outputs);
        if (onDesignOutputsGenerated) {
          onDesignOutputsGenerated(data.design_outputs);
        }
      } else {
        throw new Error('Invalid response format from AI service');
      }
    } catch (err: any) {
      console.error('Error generating design outputs:', err);
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate design outputs. Please try again.';
      setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    setComponentName('');
    setError(null);
    setGeneratedOutputs([]);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Generate Design Outputs"
      size="lg"
      footer={
        <div className="flex justify-end gap-2">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isGenerating}
          >
            {generatedOutputs.length > 0 ? 'Close' : 'Cancel'}
          </Button>
          {generatedOutputs.length === 0 && (
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !componentName.trim()}
            >
              {isGenerating ? 'Generating...' : 'Generate'}
            </Button>
          )}
        </div>
      }
    >
      <div className="space-y-4">
        {generatedOutputs.length === 0 ? (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Component Name
              </label>
              <input
                type="text"
                value={componentName}
                onChange={(e) => setComponentName(e.target.value)}
                placeholder="Enter component name (e.g., 'Blood Pressure Monitor', 'Infusion Pump')"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isGenerating}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !isGenerating && componentName.trim()) {
                    handleGenerate();
                  }
                }}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {isGenerating && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-700">Generating 5 AI design outputs...</span>
              </div>
            )}
          </>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm text-green-800 font-medium">
                Successfully generated 5 design outputs for "{componentName}"
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Generated Design Outputs:</h3>
              {generatedOutputs.map((output, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 border border-gray-200 rounded-md"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">
                      {index + 1}. {output.title || `Design Output ${index + 1}`}
                    </h4>
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {output.specification || output.description || 'No specification specified'}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default GenerateDesignOutputsModal;

