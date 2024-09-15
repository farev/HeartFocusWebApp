import numpy as np
from collections import deque

class HeartRateMonitor:
    def __init__(self, window_size=30):
        # A deque to store the last 'window_size' heart rate values
        self.heart_rate_data = deque(maxlen=window_size)

    def filter_heart_rate(self, new_bpm):
        # Only accept heart rates between 50 and 200 BPM
        if 50 <= new_bpm <= 200:
            self.heart_rate_data.append(new_bpm)
        
        # If there's no valid heart rate data, return None
        if len(self.heart_rate_data) == 0:
            return None
        
        # Return the rolling average of the heart rate values
        return np.mean(self.heart_rate_data)


