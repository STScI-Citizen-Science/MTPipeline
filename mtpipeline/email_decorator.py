"""This is the module for the email_decorator function. 

This module contains the email_decorator function which is used to 
provide updates when code completes or crashes.

Authors:
    Alex Viana, April 2014
"""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from get_settings import SETTINGS

import smtplib


def email_decorator(func):
    """Decorator to add email updates to any function.

    This function decorator will wrap any existing function and send 
    out an email when the function has completed running. If the 
    function completes normally a brief message will be sent. If the 
    the function crashes the error message will be included. 

    Parameters: 
        func : function
            The function to decorate.

    Returns: 
        wrapped : function
            The decorated function.

    Outputs:
        nothing
    """
    if SETTINGS['email_switch']:
        def wrapped(*a, **kw):
            msg = MIMEMultipart()
            msg["From"] = SETTINGS['contact_email']
            msg["To"] = SETTINGS['contact_email']
            try:
                func(*a, **kw)
                msg["Subject"] = "Process Completed"
                msg.attach(MIMEText("Process Completed"))
            except * as err:
                msg["Subject"] = "Process Crashed"
                msg.attach(MIMEText("Process Crashed: {}".format(err.message)))
            finally:
                s = smtplib.SMTP("smtp.stsci.edu")
                s.sendmail(SETTINGS['contact_email'], 
                           [SETTINGS['contact_email']], msg.as_string())
                s.quit()
    else:
        wrapped = func
    return wrapped
