import requests, socket, datetime
from datetime import timedelta

class Time:
    def timestamp_generate(time_string):
        """
        Generates a Discord timestamp based on a given time string.

        Parameters:
            time_string (str): A string representing a time in the format 'YYYY-MM-DD HH:MM:SS'.

        Returns:
            discord_timestamp (str): A Discord timestamp in the format '<t:timestamp:R>'.
        """
        dt = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        timestamp = int(dt.timestamp())
        discord_timestamp = f"<t:{timestamp}:R>"
        return discord_timestamp

    def timedelta_convert(time_string):
        """
        Convert a time string to a timedelta object.

        Parameters:
            time_string (str): The time string to be converted.

        Returns:
            timedelta: The converted timedelta object.

        Raises:
            ValueError: If the time string is invalid.
        """
        time_string = time_string.lower()

        if 'secs' in time_string:
            seconds = int(time_string.split()[0])
            return timedelta(seconds=seconds)
        elif 'mins' in time_string:
            minutes = int(time_string.split()[0])
            return timedelta(minutes=minutes)
        elif 'hour' in time_string:
            return timedelta(hours=1)
        elif 'day' in time_string:
            return timedelta(days=1)
        elif 'week' in time_string:
            return timedelta(weeks=1)
        else:
            raise ValueError("Invalid time string")
        
    def format_timedelta(duration):
        """
        Formats a timedelta object into a human-readable string representation.
        
        Args:
            duration (timedelta): The timedelta object to be formatted.
        
        Returns:
            str: A string representation of the timedelta object, formatted as 'X days, X hours, X minutes, X seconds'.
        """
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days} {'day' if days == 1 else 'days'}")
        if hours > 0:
            parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
        if minutes > 0:
            parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
        if seconds > 0:
            parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

        return ', '.join(parts)

class Info:
    
    def is_valid_discord_webhook(url):
        """
        Check if a Discord webhook URL is valid.

        Args:
            url (str): The URL of the Discord webhook to check.

        Returns:
            bool: True if the webhook URL is valid, False otherwise.
        """
        response = requests.head(url)
        return response.status_code == 200 and response.headers.get('Content-Type') == 'application/json'
    
    def ipinfo(address):
        """
        Retrieves information about an IP address using the ip-api.com service.

        Parameters:
            address (str): The IP address to retrieve information for.

        Returns:
            tuple: A tuple containing country, city, zipcode, ISP, timezone, latitude,
                   longtitude, location, hostname, prox, asn, and regioname if the 
                   information is successfully retrieved. Otherwise, returns an error message.
        """

        url = f"http://ip-api.com/json/{address}"
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "success":
            country = data["country"]
            city = data["city"]
            zipcode = data["zip"]
            isp = data["isp"]
            timezone = data["timezone"]
            latitude = data["lat"]
            longtitude = data["lon"]
            asn = data["as"]
            location = f"https://earth.google.com/web/search/{latitude}+{longtitude}"
            regioname = data["regionName"]

            if "proxy" in data:
                prox = "True"
            else:
                prox = "False"

            hostname = socket.gethostbyaddr(address)[0]
            
            return country, city, zipcode, isp, timezone, latitude, longtitude, location, hostname, prox, asn, regioname
            
        else:
            error = "❌ Invalid IP/Error."
            return error