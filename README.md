# Luma Calendar Automation

This Python script automates Luma calendar tasks including login, calendar creation, event discovery with geographic filtering, and adding events to calendars with deduplication.

## Features

- Discover events by geographic location (city name or zip code) -> right now it focuses on SF. 
- Add events to calendars with deduplication to avoid adding duplicate events
- Command-line interface with various configuration options

## Requirements

- Python 3.6 or higher
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone or download this repository to your local machine.

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Make sure you have Chrome browser installed.

4. Download the appropriate ChromeDriver for your Chrome version from [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/) and place it in your PATH.

## Usage

### Basic Usage

```bash
python luma_calendar_automation.py --location "San Francisco Bay Area" --email your.email@example.com
```

### Command-line Options

```
usage: luma_calendar_automation.py [-h] [--auth {email,google}] [--email EMAIL]
                                  [--password PASSWORD] [--calendar-name CALENDAR_NAME]
                                  --location LOCATION [--max-events MAX_EVENTS] [--headless]

Luma Calendar Automation Script

optional arguments:
  -h, --help            show this help message and exit
  --auth {email,google}  Authentication method (email or google)
  --email EMAIL         Email address for login
  --password PASSWORD   Password for login
  --calendar-name CALENDAR_NAME
                        Custom calendar name (default: Carol_YYYY-MM-DD)
  --location LOCATION   Geographic location for event filtering (city name or zip code)
  --max-events MAX_EVENTS
                        Maximum number of events to add (default: 50)
  --headless            Run browser in headless mode
```

### Examples

1. Login with email and add events from San Francisco Bay Area:

```bash
python luma_calendar_automation.py --location "San Francisco Bay Area" --auth email --email your.email@example.com
```

2. Login with Google and add events from a specific zip code:

```bash
python luma_calendar_automation.py --location "94105" --auth google --email your.gmail@gmail.com
```

3. Specify a custom calendar name:

```bash
python luma_calendar_automation.py --location "New York" --calendar-name "NYC Events" --email your.email@example.com
```

4. Limit the number of events to add:

```bash
python luma_calendar_automation.py --location "Chicago" --max-events 20 --email your.email@example.com
```

5. Run in headless mode (no visible browser window):

```bash
python luma_calendar_automation.py --location "Los Angeles" --headless --email your.email@example.com
```

## Security Notes

- The script will prompt for your password if not provided as a command-line argument
- For better security, avoid passing your password as a command-line argument
- The script stores processed events in a local JSON file for deduplication purposes

## Running Tests

To run the test suite:

```bash
python test_luma_automation.py
```

By default, tests run with mock drivers. To run with real browser:

```bash
USE_MOCK=false LUMA_EMAIL=your.email@example.com LUMA_PASSWORD=your_password python test_luma_automation.py
```

## Script Components

- `luma_authenticator.py`: Handles authentication to Luma
- `luma_calendar_manager.py`: Manages calendar creation and operations
- `luma_event_discoverer.py`: Discovers and filters events
- `luma_event_processor.py`: Adds events to calendars with deduplication
- `luma_calendar_automation.py`: Main script that integrates all components

## Scheduling the Script

### Using Cron (Linux/Mac)

To run the script daily at 8 AM:

1. Open your crontab:

```bash
crontab -e
```

2. Add the following line:

```
0 8 * * * cd /path/to/script/directory && python luma_calendar_automation.py --location "San Francisco Bay Area" --email your.email@example.com --headless >> /path/to/logfile.log 2>&1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger to Daily
4. Set the action to Start a Program
5. Program/script: `python`
6. Add arguments: `luma_calendar_automation.py --location "San Francisco Bay Area" --email your.email@example.com --headless`
7. Start in: `C:\path\to\script\directory`

## Troubleshooting

### Common Issues

1. **ChromeDriver version mismatch**:
   - Error: "This version of ChromeDriver only supports Chrome version XX"
   - Solution: Download the matching ChromeDriver version from [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/)

2. **Authentication failures**:
   - Error: "Login failed"
   - Solution: Check your credentials and ensure you have access to Luma

3. **No events found**:
   - Error: "No events found"
   - Solution: Try a different location or check if there are events available in the specified area

4. **Browser automation issues**:
   - Error: "Element not found" or "Timeout"
   - Solution: Luma's website structure might have changed. Check for updates to this script or adjust the selectors in the code.

### Logs

The script creates a log file `luma_automation.log` with detailed information about the execution. Check this file for troubleshooting.

## Customization

You can modify the script to fit your specific needs:

- Edit `luma_calendar_automation.py` to change the default behavior
- Modify the component files to adjust how the script interacts with Luma
- Add additional features by extending the existing classes

## Limitations

- The script relies on Luma's web interface, which may change over time
- Captchas or other anti-automation measures may affect the script's functionality
- Performance depends on your internet connection and the responsiveness of Luma's servers

## License

This script is provided for personal use only. Please respect Luma's terms of service when using this automation.
