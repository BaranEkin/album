import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextBrowser


class TextBrowserDate(QTextBrowser):
    def __init__(self, parent=None):
        super(TextBrowserDate, self).__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)

    # Override the contextMenuEvent method to do nothing
    def contextMenuEvent(self, event):
        pass

    def set_text(self, line_height, text):
        self.setHtml(f'<div style="line-height:{line_height}px;">{text}</div>')

    def set_date(self, line_height, date_text, date_est):
        self.set_text(line_height, TextBrowserDate.date_to_display(date_text, date_est))

    @staticmethod
    def date_to_display(date_str, precision=7):
        # Convert the date string to a datetime object
        date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        year = date_obj.strftime("%Y")
        if precision == 1:
            return f"{year}"

        else:
            month_names = {
                1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
            }
            month = month_names[date_obj.month]
            if precision == 3:
                return f"{month} {year}"
            else:
                # Extract day, month name, and year information
                day = date_obj.strftime("%d")

                # Determine the day of the week
                week_days = {
                    0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"
                }
                week_day = week_days[date_obj.weekday()]

                # Return the result in the desired format
                return f"{day} {month} {year} {week_day}"
