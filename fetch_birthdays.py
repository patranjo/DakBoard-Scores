import json
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
CALENDAR_ID = 'momsphotoframe517@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Get credentials from environment variable or file."""
    # Try environment variable first (for GitHub Actions)
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_info = json.loads(creds_json)
    else:
        # Fall back to file (for local testing)
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
    
    return service_account.Credentials.from_service_account_info(
        creds_info, scopes=SCOPES
    )

def fetch_birthdays():
    """Fetch upcoming birthdays from Google Calendar."""
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)
    
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=365)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime',
        maxResults=8
    ).execute()
    
    events = events_result.get('items', [])
    
    birthdays = []
    for event in events:
        name = event.get('summary', 'Unknown')
        start = event['start'].get('date', event['start'].get('dateTime', ''))
        
        if start:
            # Parse the date
            if 'T' in start:
                date_obj = datetime.fromisoformat(start.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(start, '%Y-%m-%d')
            
            formatted_date = date_obj.strftime('%b %d')
            birthdays.append({'name': name, 'date': formatted_date})
    
    return birthdays

def generate_html(birthdays):
    """Generate the HTML page with birthdays."""
    
    if birthdays:
        birthday_items = '\n'.join([
            f'      <div class="birthday-item"><span class="name">{b["name"]}</span><span class="date">{b["date"]}</span></div>'
            for b in birthdays
        ])
    else:
        birthday_items = '      <div class="none">No upcoming birthdays</div>'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Birthdays</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Quicksand', sans-serif;
      background: transparent;
      color: #fff;
      padding: 10px 14px;
      min-height: 100vh;
    }}

    h1 {{
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 8px;
      padding-bottom: 6px;
      border-bottom: 2px solid #fff;
      letter-spacing: 0.5px;
    }}

    .birthday-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
    }}

    .birthday-item {{
      display: flex;
      justify-content: space-between;
      font-size: 18px;
      font-weight: 500;
    }}

    .name {{
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-right: 12px;
    }}

    .date {{
      opacity: 0.85;
      white-space: nowrap;
    }}

    .none {{
      font-size: 16px;
      opacity: 0.7;
    }}
  </style>
</head>
<body>
  <h1>Birthdays</h1>
  <div class="birthday-list">
{birthday_items}
  </div>
</body>
</html>'''
    
    return html

def main():
    print("Fetching birthdays...")
    birthdays = fetch_birthdays()
    print(f"Found {len(birthdays)} upcoming birthdays")
    
    html = generate_html(birthdays)
    
    with open('birthdays.html', 'w') as f:
        f.write(html)
    
    print("Generated birthdays.html")

if __name__ == '__main__':
    main()
