import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# Function to send email notification for temperature
def send_email_notification(temp):
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Temperature Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"The current temperature is {temp}. Would you like to turn on the fan?"
    html = f"""\
        <html>
        <head>
            <style>
            .container {{
                padding: 20px;
                font-family: Arial, sans-serif;
                text-align: center; /* Center-align the content */
            }}
            .message {{
                margin-bottom: 20px;
            }}
            .a {{
                display: inline-block; /* Display the buttons in a block */
            }}
            .a {{
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                margin: 5px; /* Add margin between buttons */
                display: inline-block; /* Display buttons in a line */
            }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="message">
                <p>The current temperature is {temp}. Would you like to turn on the fan?</p>
            </div>
            <div class="buttons">
                  <p><a href="http://127.0.0.1:5000/confirm_fan?choice=yes" class="email-link">Yes, turn on the fan</a></p>
                  <p><a href="http://127.0.0.1:5000/confirm_fan?choice=no" class="email-link">No, keep it off</a></p>
            </div>
            </div>
        </body>
        </html>
        """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP("smtp.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to send email notification for light
def send_light_notification(light_intensity):
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Light Alert"

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    body = f"The Light is ON at {current_time} time. Light Intensity: {light_intensity}"

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
