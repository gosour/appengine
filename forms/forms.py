import webapp2
import cgi #for escaping html

form = """
<form method="post">
    What is your birthday?
    <br>
    <label>
        Month
        <input type="text" name="month" value="%(month)s">
    </label>
    <label>
        Day
        <input type="text" name="day" value="%(day)s">
    </label>
    <label>
        Year
        <input type="text" name="year" value="%(year)s">
    </label>
    <div style="color: red">%(error)s</div>
    <br><br>
    <input type="submit">
</form>
"""

def valid_day(day):
    try:
        int(day)
    except ValueError:
        return None
    else:
        if int(day) <= 31 and int(day) >=1:
            return int(day)
        else:
            return None

def valid_year(year):
    if year.isdigit() and int(year) in range(1900, 2021):
        return int(year)
    else: return None

def valid_month(month):
    months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
    if month.lower() in [m.lower() for m in months]:
        return months[ [m.lower() for m in months].index(month.lower()) ]
    else:
        return None



class MainPage(webapp2.RequestHandler):
    def write_form(self,error='',month='',day='',year=''):
        self.response.write(form %{
                                    "error":error,
                                    "month":month,
                                    "year":year,
                                    "day":day
                                    })
    def get(self):
        self.write_form()
   
    def post(self): #when we post our form
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = valid_month(user_month)
        year = valid_year(user_year)
        day = valid_day(user_day)
        if not(month and year and day):
            self.write_form(error="THIS IS NOT WHAT I WANT! GODDAMIT!",
                            day=cgi.escape(user_day,quote=True),
                            month=cgi.escape(user_month,quote=True),
                            year=cgi.escape(user_year,quote=True))
        else:
            self.redirect('/thanks')      
class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<b>You are awesome at entering the right date</b>')

app = webapp2.WSGIApplication([('/', MainPage),('/thanks',ThanksHandler)],debug=True)
