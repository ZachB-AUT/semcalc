from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional

@dataclass
class Session:
    """Represents a single class session (lecture, lab, etc.)"""
    starting_date: datetime
    ending_date: datetime
    day: str
    start_time: time
    end_time: time
    room: str

    @classmethod
    def from_dict(cls, session_dict: dict, sample_week: int = 3) -> Optional['Session']:
        """Create a Session instance from a dictionary (JSON data)"""
        # Convert date strings to datetime objects and calculate sample week
        starting = datetime.strptime(session_dict['starting'], '%d-%b-%Y')
        ending = datetime.strptime(session_dict['ending'], '%d-%b-%Y')

        # Calculate sample week dates
        sample_start = starting + timedelta(weeks=sample_week-1)
        sample_end = sample_start + timedelta(days=6)

        # Skip if session doesn't exist in sample week
        if sample_start > ending or sample_end < starting:
            return None

        # Parse time string with error handling
        try:
            # Try standard format "4:00 PM - 6:00 PM"
            start_str, end_str = session_dict['time'].split(' - ')
        except ValueError:
            # If that fails, print the problematic time string and raise informative error
            print(f"Error parsing time string: '{session_dict['time']}' for session in room {session_dict['room']}")
            print(f"Full session data: {session_dict}")
            raise ValueError(f"Invalid time format in session data. Expected format 'HH:MM AM/PM - HH:MM AM/PM' but got '{session_dict['time']}'")

        try:
            start_time = datetime.strptime(start_str, '%I:%M %p').time()
            end_time = datetime.strptime(end_str, '%I:%M %p').time()
        except ValueError:
            print(f"Error parsing time values: start='{start_str}', end='{end_str}'")
            raise ValueError(f"Could not parse time values. Expected format 'HH:MM AM/PM'")

        return cls(
            starting_date=starting,
            ending_date=ending,
            day=session_dict['day'],
            start_time=start_time,
            end_time=end_time,
            room=session_dict['room']
        )

    def conflicts_with(self, other: 'Session') -> bool:
        """Check if this session conflicts with another session"""
        # Different days don't conflict
        if self.day != other.day:
            return False

        # Check if date ranges overlap
        if (self.ending_date < other.starting_date or
                other.ending_date < self.starting_date):
            return False

        # Convert times to minutes for easier comparison
        self_start = self.start_time.hour * 60 + self.start_time.minute
        self_end = self.end_time.hour * 60 + self.end_time.minute
        other_start = other.start_time.hour * 60 + other.start_time.minute
        other_end = other.end_time.hour * 60 + other.end_time.minute

        # Check for overlap
        return (self_start < other_end and other_start < self_end)
