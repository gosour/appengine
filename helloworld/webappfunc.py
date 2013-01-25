"""
All the extra python functions that this app uses
"""

import re
import hashlib
import hmac

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

def rot13fy(text):
    """
    Takes in a text and returns the ROT13 cipher of it
    """
    lowers = [i+13 for i in range(ord('a'), ord('z') +1) if (i+13)<=ord('z')]
    lowers = lowers + [(i+13)%ord('z')+ord('a') -1 for i in range(ord('a'), ord('z') +1) if (i+13)>ord('z')]
    uppers = [i+13 for i in range(ord('A'), ord('Z') +1) if (i+13)<=ord('Z')]
    uppers = uppers + [(i+13)%ord('Z')+ord('A') -1 for i in range(ord('A'), ord('Z') +1) if (i+13)>ord('z')]

    lowerdict = dict(map(lambda (x,y): (chr(x),chr(y)), zip([org for org in range(ord('a'),ord('z')+1)],lowers)))
    upperdict = dict(map(lambda (x,y): (chr(x),chr(y)), zip([org for org in range(ord('A'),ord('Z')+1)],uppers)))

    totaldict = dict(lowerdict.items()+upperdict.items())

    newtext = ''
    for char in text:
        if char in totaldict:
          newtext = newtext + totaldict[char]
        else:
          newtext = newtext + char

    return newtext

def valid_username(username):
    """
    Takes a username. Return True if valid 
    False otherwise
    """
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and USER_RE.match(username)

def valid_password(password):
    """Takes a password. Returns True if valid.
    False otherwise
    """
    PASS_RE = re.compile(r"^.{3,20}$")
    return password and PASS_RE.match(password)

def valid_email(email):
    """Takes an email. Returns True if valid.
    False otherwise
    """
    EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return not email or EMAIL_RE.match(email)

def hash_str(text):
    """Takes a string and hashes it with SECRET and returns the hexdump
    """
    SECRET = "gosour"
    return hmac.new(SECRET,text).hexdigest()

def set_cookie(user):
    """Takes a username and returns a cookie string
    a cookie string: username|hashes
    """
    return '%s|%s' %(user,hash_str(user))

def valid_cookie(cookie):
    """Takes a cookie string and returns username if valid and None otherwise
    """
    if cookie:
        name = cookie.split('|',1)[0]
    else:
        return None
    if cookie == set_cookie(name):
        return name
    else:
        return None

