import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import usageTrackingService from '../services/usageTrackingService';

interface AIGenerationResult {
  success: boolean;
  message?: string;
  canGenerate: boolean;
  remainingGenerations: number;
}

export const useAIGeneration = () => {
  const { user } = useAuth();
  const [isGenerating, setIsGenerating] = useState(false);

  const checkGenerationLimit = useCallback((): AIGenerationResult => {
    if (!user) {
      return {
        success: false,
        message: 'User not authenticated',
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    const trialStatus = usageTrackingService.getTrialStatus(user.email);
    
    if (trialStatus.isLimitReached) {
      return {
        success: false,
        message: usageTrackingService.getTrialMessage(user.email),
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    return {
      success: true,
      canGenerate: true,
      remainingGenerations: trialStatus.remainingToday
    };
  }, [user]);

  const recordGeneration = useCallback((): AIGenerationResult => {
    if (!user) {
      return {
        success: false,
        message: 'User not authenticated',
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    const canGenerate = usageTrackingService.canPerformAIGeneration(user.email);
    
    if (!canGenerate) {
      return {
        success: false,
        message: usageTrackingService.getTrialMessage(user.email),
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    // Record the generation
    const success = usageTrackingService.recordAIGeneration(user.email);
    
    if (!success) {
      return {
        success: false,
        message: 'Failed to record AI generation',
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    // Get updated status
    const trialStatus = usageTrackingService.getTrialStatus(user.email);
    
    return {
      success: true,
      canGenerate: !trialStatus.isLimitReached,
      remainingGenerations: trialStatus.remainingToday
    };
  }, [user]);

  const performAIGeneration = useCallback(async (
    generationFunction: () => Promise<any>
  ): Promise<AIGenerationResult & { data?: any }> => {
    if (!user) {
      return {
        success: false,
        message: 'User not authenticated',
        canGenerate: false,
        remainingGenerations: 0
      };
    }

    // Check if user can generate
    const limitCheck = checkGenerationLimit();
    if (!limitCheck.canGenerate) {
      return limitCheck;
    }

    setIsGenerating(true);
    
    try {
      // Record the generation attempt
      const recordResult = recordGeneration();
      if (!recordResult.success) {
        return recordResult;
      }

      // Perform the actual AI generation
      const data = await generationFunction();
      
      return {
        ...recordResult,
        data
      };
    } catch (error) {
      console.error('AI generation error:', error);
      return {
        success: false,
        message: 'AI generation failed. Please try again.',
        canGenerate: true,
        remainingGenerations: usageTrackingService.getTrialStatus(user.email).remainingToday
      };
    } finally {
      setIsGenerating(false);
    }
  }, [user, checkGenerationLimit, recordGeneration]);

  const getTrialMessage = useCallback((): string => {
    if (!user) return '';
    return usageTrackingService.getTrialMessage(user.email);
  }, [user]);

  const getTrialStatus = useCallback(() => {
    if (!user) return null;
    return usageTrackingService.getTrialStatus(user.email);
  }, [user]);

  return {
    isGenerating,
    checkGenerationLimit,
    recordGeneration,
    performAIGeneration,
    getTrialMessage,
    getTrialStatus
  };
};
