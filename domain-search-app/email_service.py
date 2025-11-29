"""
Email service for sending OTP codes
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


class EmailService:
    """Service class for sending emails"""
    
    @staticmethod
    def send_otp_email(to_email, otp_code):
        """
        Send OTP code via email
        Returns: (success, message)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your OTP Code'
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = to_email
            
            # Create HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .otp-code {{
                        background: white;
                        border: 2px dashed #667eea;
                        padding: 20px;
                        text-align: center;
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #667eea;
                        margin: 20px 0;
                        border-radius: 8px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        color: #666;
                        font-size: 12px;
                    }}
                    .warning {{
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 12px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Verification Code</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>You requested a one-time password (OTP) to verify your email address. Please use the code below:</p>
                        
                        <div class="otp-code">
                            {otp_code}
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Important:</strong> This code will expire in 10 minutes. Do not share this code with anyone.
                        </div>
                        
                        <p>If you didn't request this code, please ignore this email.</p>
                        
                        <div class="footer">
                            <p>This is an automated message, please do not reply.</p>
                            <p>&copy; 2025 Domain Search App. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text = f"""
            Verification Code
            
            Hello,
            
            You requested a one-time password (OTP) to verify your email address.
            
            Your OTP code is: {otp_code}
            
            This code will expire in 10 minutes. Do not share this code with anyone.
            
            If you didn't request this code, please ignore this email.
            
            This is an automated message, please do not reply.
            """
            
            # Attach both versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            if Config.EMAIL_BACKEND == 'smtp':
                return EmailService._send_via_smtp(msg, to_email)
            elif Config.EMAIL_BACKEND == 'console':
                # For development - just print to console
                print("\n" + "="*60)
                print("📧 EMAIL (Console Backend)")
                print("="*60)
                print(f"To: {to_email}")
                print(f"Subject: {msg['Subject']}")
                print(f"OTP Code: {otp_code}")
                print("="*60 + "\n")
                return True, 'OTP sent (console mode)'
            else:
                return False, 'Invalid email backend configuration'
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False, f'Failed to send email: {str(e)}'
    
    @staticmethod
    def _send_via_smtp(msg, to_email):
        """Send email via SMTP"""
        try:
            # Connect to SMTP server
            if Config.EMAIL_USE_TLS:
                server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(Config.EMAIL_HOST, Config.EMAIL_PORT)
            
            # Login if credentials provided
            if Config.EMAIL_USERNAME and Config.EMAIL_PASSWORD:
                server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return True, 'OTP sent successfully'
            
        except Exception as e:
            print(f"SMTP Error: {str(e)}")
            return False, f'Failed to send email via SMTP: {str(e)}'
