// Email Repository Service
// Manages authorized email addresses for login

interface EmailRecord {
  email: string;
  name?: string;
  role?: string;
  addedDate: string;
  isActive: boolean;
}

class EmailRepository {
  private static instance: EmailRepository;
  private emails: EmailRecord[] = [];

  private constructor() {
    this.loadEmails();
  }

  static getInstance(): EmailRepository {
    if (!EmailRepository.instance) {
      EmailRepository.instance = new EmailRepository();
    }
    return EmailRepository.instance;
  }

  // Load emails from localStorage
  private loadEmails(): void {
    try {
      const stored = localStorage.getItem('authorizedEmails');
      if (stored) {
        this.emails = JSON.parse(stored);
      } else {
        // Initialize with some default emails
        this.emails = [
          {
            email: 'admin@foton.com',
            name: 'System Administrator',
            role: 'Admin',
            addedDate: new Date().toISOString(),
            isActive: true
          },
          {
            email: 'engineer@foton.com',
            name: 'Quality Engineer',
            role: 'Engineer',
            addedDate: new Date().toISOString(),
            isActive: true
          }
        ];
        this.saveEmails();
      }
    } catch (error) {
      console.error('Error loading emails:', error);
      this.emails = [];
    }
  }

  // Save emails to localStorage
  private saveEmails(): void {
    try {
      localStorage.setItem('authorizedEmails', JSON.stringify(this.emails));
    } catch (error) {
      console.error('Error saving emails:', error);
    }
  }

  // Check if email is authorized
  isEmailAuthorized(email: string): boolean {
    const emailRecord = this.emails.find(
      record => record.email.toLowerCase() === email.toLowerCase() && record.isActive
    );
    return !!emailRecord;
  }

  // Get all authorized emails
  getAllEmails(): EmailRecord[] {
    return this.emails.filter(record => record.isActive);
  }

  // Add new email
  addEmail(email: string, name?: string, role?: string): boolean {
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return false;
    }

    // Check if email already exists
    const existingEmail = this.emails.find(
      record => record.email.toLowerCase() === email.toLowerCase()
    );

    if (existingEmail) {
      // Reactivate if it was deactivated
      if (!existingEmail.isActive) {
        existingEmail.isActive = true;
        existingEmail.addedDate = new Date().toISOString();
        this.saveEmails();
        return true;
      }
      return false; // Email already exists and is active
    }

    // Add new email
    const newEmail: EmailRecord = {
      email: email.toLowerCase(),
      name: name || email.split('@')[0],
      role: role || 'User',
      addedDate: new Date().toISOString(),
      isActive: true
    };

    this.emails.push(newEmail);
    this.saveEmails();
    return true;
  }

  // Remove/deactivate email
  removeEmail(email: string): boolean {
    const emailRecord = this.emails.find(
      record => record.email.toLowerCase() === email.toLowerCase()
    );

    if (emailRecord) {
      emailRecord.isActive = false;
      this.saveEmails();
      return true;
    }
    return false;
  }

  // Update email details
  updateEmail(email: string, updates: Partial<EmailRecord>): boolean {
    const emailRecord = this.emails.find(
      record => record.email.toLowerCase() === email.toLowerCase()
    );

    if (emailRecord) {
      Object.assign(emailRecord, updates);
      this.saveEmails();
      return true;
    }
    return false;
  }

  // Get email statistics
  getStats(): { total: number; active: number; inactive: number } {
    const total = this.emails.length;
    const active = this.emails.filter(record => record.isActive).length;
    const inactive = total - active;
    return { total, active, inactive };
  }

  // Export emails (for backup)
  exportEmails(): string {
    return JSON.stringify(this.emails, null, 2);
  }

  // Import emails (for restore)
  importEmails(jsonData: string): boolean {
    try {
      const importedEmails = JSON.parse(jsonData);
      if (Array.isArray(importedEmails)) {
        this.emails = importedEmails;
        this.saveEmails();
        return true;
      }
    } catch (error) {
      console.error('Error importing emails:', error);
    }
    return false;
  }
}

export default EmailRepository.getInstance();
