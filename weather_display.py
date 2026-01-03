#!/usr/bin/env python3
"""
Modern 7-Day Weather Display for Raspberry Pi
Designed for 1024x600 7" touchscreen
"""

import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageTk, ImageDraw
import json
import os

class WeatherDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Display")
        
        # Configuration
        self.API_KEY = os.environ.get('WEATHER_API_KEY', '')
        self.CITY = os.environ.get('WEATHER_CITY', 'London')
        self.UNITS = 'metric'  # or 'imperial'
        
        # Setup fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#0a0e27')
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))
        
        # Main container
        self.main_frame = tk.Frame(root, bg='#0a0e27')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.setup_ui()
        self.update_weather()
        
    def setup_ui(self):
        # Header with current weather
        self.header = tk.Frame(self.main_frame, bg='#0a0e27')
        self.header.pack(fill=tk.X, pady=(0, 20))
        
        # City and time
        self.city_label = tk.Label(
            self.header,
            text=self.CITY,
            font=('Arial', 32, 'bold'),
            bg='#0a0e27',
            fg='#ffffff'
        )
        self.city_label.pack(anchor='w')
        
        self.time_label = tk.Label(
            self.header,
            text='',
            font=('Arial', 14),
            bg='#0a0e27',
            fg='#8892b0'
        )
        self.time_label.pack(anchor='w')
        
        # Current weather container
        self.current_frame = tk.Frame(self.main_frame, bg='#1a1f3a', highlightthickness=0)
        self.current_frame.pack(fill=tk.X, pady=(0, 20))
        
        current_inner = tk.Frame(self.current_frame, bg='#1a1f3a')
        current_inner.pack(padx=30, pady=30)
        
        # Temperature
        self.temp_label = tk.Label(
            current_inner,
            text='--°',
            font=('Arial', 72, 'bold'),
            bg='#1a1f3a',
            fg='#64ffda'
        )
        self.temp_label.grid(row=0, column=0, rowspan=2, padx=(0, 40))
        
        # Weather description
        self.desc_label = tk.Label(
            current_inner,
            text='Loading...',
            font=('Arial', 20),
            bg='#1a1f3a',
            fg='#ffffff'
        )
        self.desc_label.grid(row=0, column=1, sticky='sw', pady=(0, 5))
        
        # Additional info
        self.info_label = tk.Label(
            current_inner,
            text='',
            font=('Arial', 14),
            bg='#1a1f3a',
            fg='#8892b0'
        )
        self.info_label.grid(row=1, column=1, sticky='nw')
        
        # 7-day forecast
        forecast_label = tk.Label(
            self.main_frame,
            text='7-Day Forecast',
            font=('Arial', 18, 'bold'),
            bg='#0a0e27',
            fg='#ffffff'
        )
        forecast_label.pack(anchor='w', pady=(0, 10))
        
        self.forecast_frame = tk.Frame(self.main_frame, bg='#0a0e27')
        self.forecast_frame.pack(fill=tk.BOTH, expand=True)
        
        self.day_frames = []
        for i in range(7):
            day_container = tk.Frame(
                self.forecast_frame,
                bg='#1a1f3a',
                highlightthickness=0
            )
            day_container.grid(row=0, column=i, padx=5, sticky='nsew')
            self.forecast_frame.columnconfigure(i, weight=1)
            
            day_inner = tk.Frame(day_container, bg='#1a1f3a')
            day_inner.pack(expand=True, pady=15)
            
            day_name = tk.Label(
                day_inner,
                text='',
                font=('Arial', 12, 'bold'),
                bg='#1a1f3a',
                fg='#ffffff'
            )
            day_name.pack()
            
            icon_label = tk.Label(
                day_inner,
                text='',
                font=('Arial', 24),
                bg='#1a1f3a',
                fg='#64ffda'
            )
            icon_label.pack(pady=5)
            
            temp_high = tk.Label(
                day_inner,
                text='',
                font=('Arial', 14, 'bold'),
                bg='#1a1f3a',
                fg='#ffffff'
            )
            temp_high.pack()
            
            temp_low = tk.Label(
                day_inner,
                text='',
                font=('Arial', 12),
                bg='#1a1f3a',
                fg='#8892b0'
            )
            temp_low.pack()
            
            self.day_frames.append({
                'day': day_name,
                'icon': icon_label,
                'high': temp_high,
                'low': temp_low
            })
        
        # Refresh button
        self.refresh_btn = tk.Button(
            self.main_frame,
            text='⟳ Refresh',
            font=('Arial', 12),
            bg='#1a1f3a',
            fg='#64ffda',
            activebackground='#2a2f4a',
            activeforeground='#64ffda',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.update_weather
        )
        self.refresh_btn.pack(pady=(20, 0))
        
    def get_weather_icon(self, code):
        """Convert weather code to emoji"""
        icons = {
            '01d': '☀️', '01n': '🌙',
            '02d': '⛅', '02n': '☁️',
            '03d': '☁️', '03n': '☁️',
            '04d': '☁️', '04n': '☁️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌧️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️'
        }
        return icons.get(code, '🌤️')
    
    def update_weather(self):
        """Fetch and display weather data"""
        if not self.API_KEY:
            self.desc_label.config(text='API Key Required')
            self.info_label.config(text='Set WEATHER_API_KEY environment variable')
            return
        
        try:
            # Current weather
            current_url = f'https://api.openweathermap.org/data/2.5/weather?q={self.CITY}&appid={self.API_KEY}&units={self.UNITS}'
            current_data = requests.get(current_url, timeout=10).json()
            
            if current_data.get('cod') != 200:
                raise Exception(current_data.get('message', 'API Error'))
            
            # Update current weather
            temp = round(current_data['main']['temp'])
            unit = '°C' if self.UNITS == 'metric' else '°F'
            self.temp_label.config(text=f'{temp}{unit}')
            
            desc = current_data['weather'][0]['description'].title()
            self.desc_label.config(text=desc)
            
            feels = round(current_data['main']['feels_like'])
            humidity = current_data['main']['humidity']
            wind = round(current_data['wind']['speed'])
            wind_unit = 'm/s' if self.UNITS == 'metric' else 'mph'
            
            info = f'Feels like {feels}{unit} • Humidity {humidity}% • Wind {wind} {wind_unit}'
            self.info_label.config(text=info)
            
            # Update time
            now = datetime.now().strftime('%A, %B %d, %Y • %I:%M %p')
            self.time_label.config(text=now)
            
            # 7-day forecast
            lat = current_data['coord']['lat']
            lon = current_data['coord']['lon']
            forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.API_KEY}&units={self.UNITS}'
            forecast_data = requests.get(forecast_url, timeout=10).json()
            
            # Process daily forecasts
            daily_temps = {}
            for item in forecast_data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_temps:
                    daily_temps[date] = {
                        'highs': [],
                        'lows': [],
                        'icons': [],
                        'day_name': datetime.fromtimestamp(item['dt']).strftime('%a')
                    }
                daily_temps[date]['highs'].append(item['main']['temp_max'])
                daily_temps[date]['lows'].append(item['main']['temp_min'])
                daily_temps[date]['icons'].append(item['weather'][0]['icon'])
            
            # Update display
            for i, (date, data) in enumerate(list(daily_temps.items())[:7]):
                if i < len(self.day_frames):
                    day_name = 'Today' if i == 0 else data['day_name']
                    self.day_frames[i]['day'].config(text=day_name)
                    
                    icon = self.get_weather_icon(data['icons'][0])
                    self.day_frames[i]['icon'].config(text=icon)
                    
                    high = round(max(data['highs']))
                    low = round(min(data['lows']))
                    self.day_frames[i]['high'].config(text=f'{high}{unit}')
                    self.day_frames[i]['low'].config(text=f'{low}{unit}')
            
        except Exception as e:
            print(f'Error updating weather: {e}')
            self.desc_label.config(text='Update Failed')
            self.info_label.config(text=str(e))
        
        # Schedule next update (every 10 minutes)
        self.root.after(600000, self.update_weather)

if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherDisplay(root)
    root.mainloop()
