// Usage tracking service for AI generation limits and trial management

interface UsageRecord {
  userEmail: string;
  date: string; // YYYY-MM-DD format
  aiGenerations: number;
  lastReset: string; // ISO timestamp
}

interface TrialStatus {
  isTrialUser: boolean;
  dailyLimit: number;
  usedToday: number;
  remainingToday: number;
  isLimitReached: boolean;
  resetTime: string; // Next reset time
}

class UsageTrackingService {
  private static instance: UsageTrackingService;
  private localStorageKey = 'aiUsageTracking';
  private adminEmails = ['admin@foton.com', 'john@fotonconsulting.com'];
  
  // Trial limits
  private readonly DAILY_TRIAL_LIMIT = 5;
  private readonly ADMIN_DAILY_LIMIT = 999999; // Effectively unlimited

  private constructor() {}

  static getInstance(): UsageTrackingService {
    if (!UsageTrackingService.instance) {
      UsageTrackingService.instance = new UsageTrackingService();
    }
    return UsageTrackingService.instance;
  }

  // Check if user is admin
  private isAdmin(userEmail: string): boolean {
    return this.adminEmails.includes(userEmail.toLowerCase());
  }

  // Get today's date in YYYY-MM-DD format
  private getTodayDate(): string {
    return new Date().toISOString().split('T')[0];
  }

  // Get next reset time (midnight tomorrow)
  private getNextResetTime(): string {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return tomorrow.toISOString();
  }

  // Load usage data from localStorage
  private loadUsageData(): UsageRecord[] {
    try {
      const stored = localStorage.getItem(this.localStorageKey);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error loading usage data:', error);
      return [];
    }
  }

  // Save usage data to localStorage
  private saveUsageData(usageData: UsageRecord[]): void {
    try {
      localStorage.setItem(this.localStorageKey, JSON.stringify(usageData));
    } catch (error) {
      console.error('Error saving usage data:', error);
    }
  }

  // Get or create usage record for user and date
  private getUsageRecord(userEmail: string, date: string): UsageRecord {
    const usageData = this.loadUsageData();
    const existingRecord = usageData.find(
      record => record.userEmail.toLowerCase() === userEmail.toLowerCase() && record.date === date
    );

    if (existingRecord) {
      return existingRecord;
    }

    // Create new record
    const newRecord: UsageRecord = {
      userEmail: userEmail.toLowerCase(),
      date,
      aiGenerations: 0,
      lastReset: new Date().toISOString()
    };

    usageData.push(newRecord);
    this.saveUsageData(usageData);
    return newRecord;
  }

  // Record an AI generation
  recordAIGeneration(userEmail: string): boolean {
    const today = this.getTodayDate();
    const usageData = this.loadUsageData();
    const record = this.getUsageRecord(userEmail, today);

    // Check if user has reached their limit
    const trialStatus = this.getTrialStatus(userEmail);
    if (trialStatus.isLimitReached) {
      return false; // Limit reached, cannot generate
    }

    // Increment usage
    record.aiGenerations += 1;
    record.lastReset = new Date().toISOString();

    // Update the record in the array
    const recordIndex = usageData.findIndex(
      r => r.userEmail.toLowerCase() === userEmail.toLowerCase() && r.date === today
    );
    if (recordIndex !== -1) {
      usageData[recordIndex] = record;
    } else {
      usageData.push(record);
    }

    this.saveUsageData(usageData);
    return true;
  }

  // Get trial status for a user
  getTrialStatus(userEmail: string): TrialStatus {
    const today = this.getTodayDate();
    const record = this.getUsageRecord(userEmail, today);
    const isAdmin = this.isAdmin(userEmail);
    
    const dailyLimit = isAdmin ? this.ADMIN_DAILY_LIMIT : this.DAILY_TRIAL_LIMIT;
    const usedToday = record.aiGenerations;
    const remainingToday = Math.max(0, dailyLimit - usedToday);
    const isLimitReached = !isAdmin && usedToday >= this.DAILY_TRIAL_LIMIT;

    return {
      isTrialUser: !isAdmin,
      dailyLimit,
      usedToday,
      remainingToday,
      isLimitReached,
      resetTime: this.getNextResetTime()
    };
  }

  // Get usage history for a user (last 30 days)
  getUserUsageHistory(userEmail: string): UsageRecord[] {
    const usageData = this.loadUsageData();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const cutoffDate = thirtyDaysAgo.toISOString().split('T')[0];

    return usageData
      .filter(record => 
        record.userEmail.toLowerCase() === userEmail.toLowerCase() && 
        record.date >= cutoffDate
      )
      .sort((a, b) => b.date.localeCompare(a.date));
  }

  // Reset daily usage (for testing or manual reset)
  resetDailyUsage(userEmail: string): void {
    const today = this.getTodayDate();
    const usageData = this.loadUsageData();
    const recordIndex = usageData.findIndex(
      r => r.userEmail.toLowerCase() === userEmail.toLowerCase() && r.date === today
    );

    if (recordIndex !== -1) {
      usageData[recordIndex].aiGenerations = 0;
      usageData[recordIndex].lastReset = new Date().toISOString();
      this.saveUsageData(usageData);
    }
  }

  // Get all users' usage for admin dashboard
  getAllUsersUsage(): { [userEmail: string]: UsageRecord[] } {
    const usageData = this.loadUsageData();
    const userUsage: { [userEmail: string]: UsageRecord[] } = {};

    usageData.forEach(record => {
      if (!userUsage[record.userEmail]) {
        userUsage[record.userEmail] = [];
      }
      userUsage[record.userEmail].push(record);
    });

    // Sort each user's records by date (newest first)
    Object.keys(userUsage).forEach(userEmail => {
      userUsage[userEmail].sort((a, b) => b.date.localeCompare(a.date));
    });

    return userUsage;
  }

  // Clear old usage data (older than 90 days)
  cleanupOldData(): void {
    const usageData = this.loadUsageData();
    const ninetyDaysAgo = new Date();
    ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
    const cutoffDate = ninetyDaysAgo.toISOString().split('T')[0];

    const filteredData = usageData.filter(record => record.date >= cutoffDate);
    this.saveUsageData(filteredData);
  }

  // Get trial message for user
  getTrialMessage(userEmail: string): string {
    const status = this.getTrialStatus(userEmail);
    
    if (!status.isTrialUser) {
      return "You have unlimited AI generations as an admin user.";
    }

    if (status.isLimitReached) {
      return `🚫 Trial limit reached! You've used all ${status.dailyLimit} AI generations for today. Contact your administrator for additional or unlimited access.`;
    }

    if (status.remainingToday <= 2) {
      return `⚠️ Warning: You have ${status.remainingToday} AI generations remaining today. Contact your administrator for additional access.`;
    }

    return `✅ You have ${status.remainingToday} AI generations remaining today.`;
  }

  // Check if user can perform AI generation
  canPerformAIGeneration(userEmail: string): boolean {
    const status = this.getTrialStatus(userEmail);
    return !status.isLimitReached;
  }
}

export default UsageTrackingService.getInstance();
