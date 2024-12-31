from flask import Flask, render_template, jsonify
import pandas as pd
from datetime import datetime
import os

calendarApp = Flask(__name__)

# Read and combine Excelsheets of various calendars
def get_combined_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    files = {
        "project_schedules": os.path.join(BASE_DIR, "CalendarData", "project_schedule.xlsx"),
        "holidays": os.path.join(BASE_DIR, "CalendarData", "holidays.xlsx"),
        "employee_vacations": os.path.join(BASE_DIR, "CalendarData", "employee_vacations.xlsx"),
        "audit_days": os.path.join(BASE_DIR, "CalendarData", "schedule_audit.xlsx"),
    }

    dataframes = []
    for category, file in files.items():
        if not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")
        df = pd.read_excel(file)

        # Handle vacations separately to exclude weekends
        if category == "employee_vacations":
            vacation_events = []
            for _, row in df.iterrows():
                start_date = pd.to_datetime(row['Start Date'])
                end_date = pd.to_datetime(row['End Date'])

                # Generate an entry for each weekday in the vacation range
                date_range = pd.date_range(start=start_date, end=end_date)
                for date in date_range:
                    if date.weekday() < 5:  # Only include weekdays (Monday=0, Sunday=6)
                        vacation_events.append({
                            "Date": date,
                            "Event": f"Vacation - {row['Employee Name']}",
                            "Category": "employee_vacations"
                        })

            vacation_df = pd.DataFrame(vacation_events)
            dataframes.append(vacation_df)
        else:
            df['Category'] = category  # Add category for color coding
            dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    return combined_df

@calendarApp.route('/')
def calendar():
    return render_template('calendar.html')

@calendarApp.route('/api/events')
def events():
    combined_data = get_combined_data()
    events = [
        {
            "title": f"{row['Event']} ({row['Category']})",
            "start": row['Date'].strftime('%Y-%m-%d'),
            "color": get_color(row['Category'])
        }
        for _, row in combined_data.iterrows()
    ]
    return jsonify(events)

def get_color(category):
    color_map = {
        "project_schedules": "blue",
        "holidays": "green",
        "employee_vacations": "orange",
        "audit_days": "red"
    }
    return color_map.get(category, "gray")

if __name__ == '__main__':
    calendarApp.run(debug=True)
