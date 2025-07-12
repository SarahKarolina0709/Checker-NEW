#!/usr/bin/env python3
"""
Debug script to test calendar generation and fix the missing days issue.
"""

import calendar
from datetime import datetime
import customtkinter as ctk

def test_calendar_generation():
    """Test calendar generation with debug output"""
    try:
        print("=== Calendar Generation Debug ===")
        
        # Test current date
        current_date = datetime.now()
        print(f"Current date: {current_date}")
        print(f"Year: {current_date.year}, Month: {current_date.month}")
        
        # Test calendar generation
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        print(f"Calendar for {calendar.month_name[current_date.month]} {current_date.year}:")
        
        for week_num, week in enumerate(cal):
            print(f"Week {week_num}: {week}")
            for col, day in enumerate(week):
                if day == 0:
                    print(f"  Day {col}: Empty (0)")
                else:
                    print(f"  Day {col}: {day}")
        
        print(f"\nTotal weeks: {len(cal)}")
        print(f"Days in month: {[day for week in cal for day in week if day != 0]}")
        
        # Test with GUI
        test_gui_calendar()
        
    except Exception as e:
        print(f"Error in calendar generation: {e}")
        import traceback
        traceback.print_exc()

def test_gui_calendar():
    """Test GUI calendar to see if buttons are created"""
    print("\n=== GUI Calendar Test ===")
    
    try:
        # Create test window
        root = ctk.CTk()
        root.title("Calendar Debug Test")
        root.geometry("800x600")
        
        # Create calendar frame
        calendar_frame = ctk.CTkFrame(root, fg_color="#E5E7EB")
        calendar_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(8):  # 0=header, 1-7=weeks
            calendar_frame.grid_rowconfigure(i, weight=1)
        
        # Day headers
        days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        for i, day in enumerate(days):
            day_header = ctk.CTkLabel(
                calendar_frame,
                text=day,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#6B7280",
                height=40
            )
            day_header.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            print(f"Created header: {day} at column {i}")
        
        # Generate calendar days
        current_date = datetime.now()
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        
        button_count = 0
        row = 1
        for week in cal:
            for col, day in enumerate(week):
                if day == 0:
                    print(f"Skipping empty day at row {row}, col {col}")
                    continue
                
                # Create day button
                day_btn = ctk.CTkButton(
                    calendar_frame,
                    text=str(day),
                    width=80,
                    height=60,
                    fg_color="#FFFFFF",
                    text_color="#000000",
                    hover_color="#F3F4F6",
                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    border_width=1,
                    border_color="#D1D5DB"
                )
                day_btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
                button_count += 1
                print(f"Created button for day {day} at row {row}, col {col}")
            
            row += 1
        
        print(f"\nTotal buttons created: {button_count}")
        
        # Add close button
        close_btn = ctk.CTkButton(
            root,
            text="Schließen",
            command=root.destroy,
            height=40
        )
        close_btn.pack(pady=10)
        
        # Show window
        root.mainloop()
        
    except Exception as e:
        print(f"Error in GUI calendar test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_generation()
