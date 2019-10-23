"""Script: BookMyClass.py
     Desc: An example Python + Selenium script to automate class booking on sites (for learning & training purposes)
  Version: 1.0
   Author: Prajwal Shetty D
     Date: 08/04/2019

   Syntax: ./BookMyClass.py <site-url> <class-type> <day-of-the-week> <site-email-or-username> <site-password> <whatsapp-number> <user-or-alias> <attempt-count>
  Example: ./BookMyClass.py https://booking.goldsgym.co.uk/CCE/ClassesAccordion.aspx ZUMBA MON abc@gmail.com xyz123 1234567890 Prajwal 1
"""

"""Libraries
"""
import datetime
import time
import smtplib
import sys
from selenium import webdriver
from time import sleep
from twilio.rest import Client

"""Timestamps, to display total time taken by the script at the end of run
"""
curr_time = time.time()
curr_timestamp = datetime.datetime.fromtimestamp(curr_time).strftime('%Y-%m-%d %H:%M:%S')

"""Set the delay in seconds (i.e. ~ delay between each browser action), 7/10th of a second seems to be the optimal setting for many sites
"""
sleep_parm = 0.7

"""Script arguments, it takes up to 7 arguments - class type, day of the week, email, password, mobile number, user, attempt-count
"""
arg_site_url = sys.argv[1]
arg_class_type = sys.argv[2]
arg_class_day_of_the_week = sys.argv[3]
arg_site_user_email = sys.argv[4]
arg_site_user_password = sys.argv[5]
arg_whatsapp_num = sys.argv[6]
arg_site_user = sys.argv[7]
arg_attempt_count = sys.argv[8]

"""Mode of alerts, supports Email and WhatsApp via Twilio
"""
send_email_alert = "Y"
send_whatsapp_alert = "Y"

"""Log
"""
print("--- Started on", curr_timestamp, "for", arg_site_user, "attempt", arg_attempt_count, "---")

"""Log
"""
print(arg_class_type, "for", arg_class_day_of_the_week)

"""Open Chrome and make the first contact
"""
driver = webdriver.Chrome()
driver.get(arg_site_url)
sleep(sleep_parm)

"""Everything below is an example of how you can use Selenium to parse a web document, you must customise it by the site you want to parse.
"""

"""Select the class day
"""
driver.find_element_by_link_text(arg_class_day_of_the_week).click()
sleep(sleep_parm)

"""Loop through the day on the site
"""
for pane_no in range(1, 10):
    site_class_type = driver.find_element_by_xpath('//*[@id="ctl00_mainContent_AccordionOcc_Pane_%d_header"]/h3/span[2]' % pane_no).text
    if site_class_type == arg_class_type:
        print(site_class_type, "class found at idx.", pane_no)
        the_pane_no = pane_no
        break

"""Now that we know the id name, go ahead and select the class and press click.
"""
driver.find_element_by_xpath('//*[@id="ctl00_mainContent_AccordionOcc_Pane_%d_header"]/h3/span[2]' % the_pane_no).click()
sleep(sleep_parm)

"""Select the class on the page
"""
driver.find_element_by_link_text("SELECT").click()
sleep(sleep_parm)

"""Add login details to the form, note that we haven't completed the login process until now!
"""
username_field = driver.find_element_by_id("ctl00_mainContent_Login1_UserName")
username_field.send_keys(str(arg_site_user_email))
password_field = driver.find_element_by_id("ctl00_mainContent_Login1_Password")
password_field.send_keys(str(arg_site_user_password))
driver.find_element_by_link_text("LOGIN").click()
sleep(sleep_parm)

"""Click on the NEXT button
"""
driver.find_element_by_link_text("NEXT →").click()
sleep(sleep_parm)

"""Possible website messages lookup variables
"""
class_already_joined_msg = "You have already joined this class"
class_successful_booking_msg = "Thank you! Your booking is confirmed"
class_join_waiting_list_msg = "Join Waiting List"
class_waiting_list_is_full_msg = "Error - Waiting list is full"
class_joined_waiting_list_msg = "Joined the waiting list"
class_advance_booking_error_msg = "You cannot make bookings that far in advance"

"""Check the message on the website after processing the booking request
"""
# If you have already joined the class, the book button won't appear
if driver.page_source.find(class_already_joined_msg) != -1:
    print(class_already_joined_msg)
    email_subject = class_already_joined_msg
    email_body = class_already_joined_msg
    sleep(sleep_parm)
else:
    # Click on the BOOK button
    driver.find_element_by_link_text("BOOK").click()
    sleep(sleep_parm)

# Check after clicking "BOOK"
if driver.page_source.find(class_successful_booking_msg) != -1:
    # Success
    print(class_successful_booking_msg)
    sleep(sleep_parm)
    email_subject = class_successful_booking_msg
    email_body = class_successful_booking_msg
elif driver.page_source.find(class_join_waiting_list_msg) != -1:
    # Waiting list
    print(class_join_waiting_list_msg)
    driver.find_element_by_xpath('//*[@id="ctl00_mainContent_DDLPreferedContactMethod1"]/option[2]').click()
    driver.find_element_by_link_text("JOIN WAITING LIST").click()
    sleep(sleep_parm)
    if driver.page_source.find(class_waiting_list_is_full_msg):
        # Waiting list is full!
        print(class_waiting_list_is_full_msg)
        email_subject = class_waiting_list_is_full_msg
        email_body = class_waiting_list_is_full_msg
    else:
        # Joined the waiting list...
        print(class_joined_waiting_list_msg)
        email_subject = class_joined_waiting_list_msg
        email_body = class_joined_waiting_list_msg
elif driver.page_source.find(class_advance_booking_error_msg) != -1:
    # Too early!
    print(class_advance_booking_error_msg)
    advance_booking_error_desc = driver.find_element_by_xpath('// *[ @ id = "ctl00_updatePanel"]/div[2]').text
    email_subject = class_advance_booking_error_msg
    email_body = advance_booking_error_desc
    sleep(sleep_parm)
else:
    if driver.page_source.find(class_already_joined_msg) == -1:
        # Something is wrong if the code reaches here
        print("The script has encountered an error...", '\n')
        print("-----start of page source dump-----")
        on_error_site_page_source_dump = driver.page_source
        print(on_error_site_page_source_dump)
        print("-----------------------------------", '\n')
        email_subject = "UNKNOWN ERROR - The website was down or the script failed!"
        email_body = on_error_site_page_source_dump
        sleep(sleep_parm)

"""Close the browser session
"""
driver.quit()

"""End timestamp
"""
curr_time = time.time()
curr_timestamp = datetime.datetime.fromtimestamp(curr_time).strftime('%Y-%m-%d %H:%M:%S')

"""Send an email (Google SMTP server is used here)
"""
email_smtp_server = "smtp.gmail.com"
to_email_address = arg_site_user_email
from_email_address = "<provide-your-email-address>"
from_email_address_pass = "<your-password>"
email_subject_prefix = "<email-title> "
if send_email_alert == "Y" and email_subject != class_already_joined_msg:
    msg = 'Subject: {}\n\n{}'.format(email_subject_prefix +
                                     "[" + arg_class_type.capitalize() + " " + arg_class_day_of_the_week.capitalize() + "]: " +
                                     email_subject, email_body)
    server = smtplib.SMTP(email_smtp_server, 587)
    server.starttls()
    server.login(from_email_address, from_email_address_pass)
    server.sendmail(from_email_address, to_email_address, msg)
    print("An email has been sent to", to_email_address)
    server.quit()

"""Send a WhatsApp message
   Uses Twilio (see https://www.twilio.com/docs/sms/whatsapp/quickstart/python)
   Your Account SID and Auth Token from http://www.twilio.com/console
   DANGER! This is insecure. See http://twil.io/secure
"""
if send_whatsapp_alert == "Y" and email_subject != class_already_joined_msg:
    account_sid = '<twilio-account-sid>'
    auth_token = '<twilio-auth-token>'
    client = Client(account_sid, auth_token)
    whatsapp_body='Your appointment is coming up on ' + arg_class_day_of_the_week + ' at ' + arg_class_type + '__' + arg_site_user + '_' + email_subject.replace(" ", "_")
    message = client.messages \
                    .create(
                         body=whatsapp_body,
                         from_='whatsapp:<twilio-whatsapp-no>',
                         to='whatsapp:' + arg_whatsapp_num,
                    )

    message = client.messages \
                    .create(
                         body=whatsapp_body,
                         from_='whatsapp:<twilio-whatsapp-no>',
                         to='whatsapp:<target-whatsapp-no>',
                    )

    print("WhatsApp alert has been sent to:", arg_whatsapp_num)

"""End
"""
print("--- Ended on", curr_timestamp, "for", arg_site_user, "attempt", arg_attempt_count, "---")
