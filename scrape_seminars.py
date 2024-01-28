import requests
from bs4 import BeautifulSoup
import datetime
import re
import pytz


error_str = "<font color='red'>ERROR!!!</font>"

##### ACADEMIA SINICA #####

# Send a GET request to the website
url = "https://www.math.sinica.edu.tw/www/seminar/seminar20_e.jsp"
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find all the seminar elements on the page
seminar_elements = soup.find_all("div", class_="card col-md-12 col-lg-6")

# Create an array to store the seminar information
seminar_info = []

fail_count = 0

for seminar in seminar_elements:
    # Initialize a dictionary to store the seminar details
    seminar_details = {}

    # Extract seminar body
    div_element = seminar.find("div", class_="card-body")
    if div_element:
        input_string = div_element.prettify().strip()
    else:
        fail_count += 1
        continue

    # Extract speaker and institution using regular expression
    pattern = r"\n(.+?) \((.*?)\)"
    match = re.search(pattern, input_string)
    if match:
        speaker = match.group(1).strip()
        institution = match.group(2).strip()
        seminar_details['speaker'] = speaker
        seminar_details['institution'] = institution
    else:
        seminar_details['speaker'] = error_str
        seminar_details['institution'] = error_str

    # Extract date and time using regular expression
    pattern = r"(\d{4}-\d{2}-\d{2})\(\w+\.\)\s+(\d{2}:\d{2})\s+-\s+(\d{2}:\d{2})"
    match = re.search(pattern, input_string)
    if match:
        date_str = match.group(1)
        start_time_str = match.group(2)
        end_time_str = match.group(3)
        # Convert date and time strings to datetime objects
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
        seminar_details['date'] = date
        seminar_details['start_time'] = start_time
        seminar_details['end_time'] = end_time
    else:
        date = datetime.datetime(1, 1, 1, 0, 0)
        seminar_details['date'] = date.date()
        seminar_details['start_time'] = date.time()
        seminar_details['end_time'] = date.time()

    # Extract location as the last piece of information in the text
    location = input_string.splitlines()[-3].strip()
    seminar_details['location'] = location

    # Extracting the title
    title = re.search(r'</noscript>\s*(.*?)\s*</a>', input_string)
    if title:
        seminar_details['title'] = title.group(1).strip()
    else:
        seminar_details['title'] = error_str
        
    # Extracting the link
    link = re.search(r"javascript:window.open\('([^']*)'", input_string)  
    if link:
        seminar_details['link'] = "https://www.math.sinica.edu.tw" + link.group(1).strip()
    else:
        seminar_details['link'] = error_str
        
    # Extract seminar name
    seminar_name = seminar.find("div", class_="card-title").text.strip()
    if seminar_name:
        seminar_details['seminar_name'] = seminar_name
    else:
        seminar_details['seminar_name'] = error_str

    # Add the seminar details to the array
    seminar_info.append(seminar_details)



##### NCTS #####

url = "https://ncts.ntu.edu.tw/events_list.php?kind=1"

response = requests.get(url)
response.encoding = "UTF-8" #Needed to get Chinese characters to display properly for some reason

soup = BeautifulSoup(response.text, "html.parser")

event_tables = soup.find_all("table", class_="events_Title-Line0")

for table in event_tables:

    text1s = table.find_all("span", class_="Text1")
    
    time_string = text1s[0].text.strip()
    # Remove ()
    time_string = re.sub(r'\([^)]*\)', '', time_string)
    time_string = time_string.strip()


    time_range = time_string.split(",")[0].strip()

    # Extract the date
    date = time_string.split(",")[1] + ", " + time_string.split(",")[2]
    date = date.strip()

    # Extract the start time and end time
    start_time, end_time = time_range.split("-")[0].strip(), time_range.split("-")[1].strip()

    # Create a datetime object for the date
    date = datetime.datetime.strptime(date, "%B %d, %Y").date()

    # Create datetime objects for the start time and end time
    start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.datetime.strptime(end_time, "%H:%M").time()

    
    link = table.find("a")["href"]
    seminar_name = text1s[2].text.strip()
    title = table.find("td", class_="Title").text.strip()
    if len(text1s) >= 4:
        speaker, institution = text1s[3].text.strip().split("\t(")
    else:
    	speaker = "n/a"
    	institution = "n/a"

    institution = institution[:-1]  # Remove the closing parenthesis
    
    link = "https://ncts.ntu.edu.tw/" + link
    
    location = text1s[1].text.strip()
    
    seminar_entry = {
        "title": title,
        "speaker": speaker,
        "institution": institution,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "link": link,
        "seminar_name": seminar_name,
        "location": location
    }
    
    seminar_info.append(seminar_entry)




##### PROCESS AND OUTPUT #####

# Specify the time zone
timezone = 'Asia/Taipei'
# Get the current time in the specified time zone
taipei_timezone = pytz.timezone(timezone)
taipei_time = datetime.datetime.now(taipei_timezone)
# Format the current time
formatted_time = taipei_time.strftime('%Y-%m-%d %H:%M')


# Sort by date
sorted_seminar_info = sorted(seminar_info, key=lambda x: (x['date'], x['start_time']))



# Generate the output HTML
output_html = '''<html><head><title>Taipei Math Seminar Autoscrape</title><meta http-equiv='Content-Type' content='text/html; charset=utf-8' />
<script>
        function displayTimeDifference() {
            var targetTime = new Date("TIMETIMETIME");
            var currentTime = new Date();
            var timeDifference = currentTime - targetTime;

            var days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
            var hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));

            var output = "";

            if (days > 1) {
                output += "<font color='red'>" + days + " days ago!</font>"
            } else if (days > 0) {
                output += days + " days ago";
            } else if (hours > 0) {
                output += hours + " hours ago";
            } else if (minutes > 0) {
                output += minutes + " minutes ago";
            } else {
                output += "just now"
            }

            document.getElementById("time-difference").innerHTML = output;
        }

        window.onload = function() {
            displayTimeDifference();
        };
    </script>

</head><body><h1>Taipei Math Seminar Autoscrape ᕕ( ᐛ )ᕗ</h1><h3>\n'''

output_html = output_html.replace("TIMETIMETIME", formatted_time)

if fail_count == 0:
    fail_count_str = "<font color='green'>0</font>"
else:
    fail_count_str = f"<b><font color='red'>{fail_count}!!!</font> Σ(°□°´Ⅲ)!!?</b>"


output_html += f"Last scrape at {timezone} {formatted_time} (<p style='display:inline' id='time-difference'></p>)"
output_html += "</h3>Scraped <a href='https://www.math.sinica.edu.tw/www/seminar/seminar20_e.jsp'>AS</a>+<a href='https://ncts.ntu.edu.tw/events_list.php?kind=1'>NCTS</a>.  Excludes conferences and courses. "
output_html += f"Fail count: {fail_count_str}<hr>\n"


# Get current week
current_week = None

for seminar in sorted_seminar_info:
    week = seminar['date'].isocalendar()[1] 
    if week != current_week:
        current_week = week
        output_html += "<hr><hr>\n"
    weekday = seminar['date'].strftime("%A")
    starttime = seminar['start_time'].strftime("%H:%M")
    endtime = seminar['end_time'].strftime("%H:%M")
    datestr = seminar['date'].strftime("%B %d, %Y")
    output_html += f"<p><b>{seminar['seminar_name']}</b><br><br>"
    output_html += f"<b>{weekday}</b> {datestr}, {starttime} to {endtime}<br>"
    output_html += f"{seminar['location']}<br><br>"
    output_html += f"<b>{seminar['speaker']}</b> ({seminar['institution']})<br>"
    output_html += f"<a href='{seminar['link']}'>{seminar['title']}</a></p>\n"
    output_html += "<hr>\n"

# Close the HTML tags
output_html += "<a href='scrape_seminars.py'>Code</a> written mostly by ChatGPT.\n<hr><a href='index.html'>back to homepage</a></body></html>"

# Save the output HTML to a file
with open("seminar_output.html", "w", encoding="utf-8") as file:
    file.write(output_html)
    
    
print("Seminar information saved to seminar_output.html")
