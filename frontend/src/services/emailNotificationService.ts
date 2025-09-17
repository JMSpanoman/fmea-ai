// Email notification service for new logons
// This service handles sending email notifications when users log in

interface LoginNotification {
  userEmail: string;
  userName: string;
  userRole: string;
  loginTime: string;
  ipAddress?: string;
  userAgent?: string;
}

class EmailNotificationService {
  private static instance: EmailNotificationService;
  private adminEmail = 'john@fotonconsulting.com';

  private constructor() {}

  static getInstance(): EmailNotificationService {
    if (!EmailNotificationService.instance) {
      EmailNotificationService.instance = new EmailNotificationService();
    }
    return EmailNotificationService.instance;
  }

  // Send login notification to admin
  async sendLoginNotification(notification: LoginNotification): Promise<void> {
    try {
      // In a real application, you would integrate with an email service like SendGrid, AWS SES, etc.
      // For now, we'll log the notification and show it in the console
      console.log('📧 LOGIN NOTIFICATION TO ADMIN:');
      console.log('================================');
      console.log(`To: ${this.adminEmail}`);
      console.log(`Subject: New User Login - Foton aiQMS`);
      console.log('');
      console.log(`A new user has logged into the Foton aiQMS system:`);
      console.log('');
      console.log(`👤 User Details:`);
      console.log(`   Email: ${notification.userEmail}`);
      console.log(`   Name: ${notification.userName}`);
      console.log(`   Role: ${notification.userRole}`);
      console.log(`   Login Time: ${notification.loginTime}`);
      if (notification.ipAddress) {
        console.log(`   IP Address: ${notification.ipAddress}`);
      }
      if (notification.userAgent) {
        console.log(`   User Agent: ${notification.userAgent}`);
      }
      console.log('');
      console.log(`🔐 Security Information:`);
      console.log(`   This login was authorized through the email management system.`);
      console.log(`   If this login was not expected, please review the user permissions.`);
      console.log('');
      console.log(`📊 System Access:`);
      console.log(`   The user now has access to all FMEA and quality management features.`);
      console.log(`   Monitor user activity through the admin dashboard.`);
      console.log('================================');

      // Store notification in localStorage for admin review
      this.storeNotification(notification);

      // In a production environment, you would send an actual email here
      // Example with a hypothetical email service:
      // await this.sendEmail({
      //   to: this.adminEmail,
      //   subject: 'New User Login - Foton aiQMS',
      //   body: this.formatEmailBody(notification)
      // });

    } catch (error) {
      console.error('Error sending login notification:', error);
    }
  }

  // Store notification for admin review
  private storeNotification(notification: LoginNotification): void {
    try {
      const notifications = this.getStoredNotifications();
      notifications.unshift(notification);
      
      // Keep only last 50 notifications
      if (notifications.length > 50) {
        notifications.splice(50);
      }
      
      localStorage.setItem('loginNotifications', JSON.stringify(notifications));
    } catch (error) {
      console.error('Error storing notification:', error);
    }
  }

  // Get stored notifications
  getStoredNotifications(): LoginNotification[] {
    try {
      const stored = localStorage.getItem('loginNotifications');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error getting stored notifications:', error);
      return [];
    }
  }

  // Clear old notifications
  clearOldNotifications(): void {
    try {
      const notifications = this.getStoredNotifications();
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
      
      const recentNotifications = notifications.filter(notification => 
        new Date(notification.loginTime) > oneWeekAgo
      );
      
      localStorage.setItem('loginNotifications', JSON.stringify(recentNotifications));
    } catch (error) {
      console.error('Error clearing old notifications:', error);
    }
  }

  // Format email body (for future email service integration)
  private formatEmailBody(notification: LoginNotification): string {
    return `
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
      🔐 New User Login - Foton aiQMS
    </h2>
    
    <p>A new user has successfully logged into the Foton aiQMS system.</p>
    
    <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
      <h3 style="color: #1e40af; margin-top: 0;">👤 User Details</h3>
      <p><strong>Email:</strong> ${notification.userEmail}</p>
      <p><strong>Name:</strong> ${notification.userName}</p>
      <p><strong>Role:</strong> ${notification.userRole}</p>
      <p><strong>Login Time:</strong> ${notification.loginTime}</p>
      ${notification.ipAddress ? `<p><strong>IP Address:</strong> ${notification.ipAddress}</p>` : ''}
    </div>
    
    <div style="background-color: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0;">
      <h3 style="color: #dc2626; margin-top: 0;">🔐 Security Information</h3>
      <p>This login was authorized through the email management system. If this login was not expected, please review the user permissions immediately.</p>
    </div>
    
    <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
      <h3 style="color: #0369a1; margin-top: 0;">📊 System Access</h3>
      <p>The user now has access to all FMEA and quality management features. Monitor user activity through the admin dashboard.</p>
    </div>
    
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
    
    <p style="font-size: 12px; color: #6b7280;">
      This is an automated notification from the Foton aiQMS system.<br>
      Generated on ${new Date().toLocaleString()}
    </p>
  </div>
</body>
</html>
    `;
  }
}

export default EmailNotificationService.getInstance();
