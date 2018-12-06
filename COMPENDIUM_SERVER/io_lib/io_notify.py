# -*- coding: utf-8 -*- 
import smtplib
import io_debug
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.charset import Charset, BASE64
from email.mime.nonmultipart import MIMENonMultipart

class io_notify:
	def __init__(self, io_print, io_log, print_All=False):
		if print_All:
			self.io_print = io_debug.io_debug(io_print, io_log).io_print
		else:
			self.io_print = io_debug.io_debug(False, io_log).io_print
		return

	# send_email: to send only a text email, msg must be a string and withAttachment False,
	# to email an interacive email with attachments withAttachment must be True.
	def send_email(self, to = '', msg = '', withAttachment = False):
		try:
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login('ioperspejimai@gmail.com','G3nerico01')
			if withAttachment:
				server.sendmail('ioperspejimai@gmail.com',to,msg.as_string())
			else:
				server.sendmail('ioperspejimai@gmail.com',to,msg)
			server.quit()
			return True
		except Exception as e:
			self.io_print('[!] Something went wrong sending email: ' + str(e))
			return False

	# Send email report after scraping the daily boletin,
	# we will create a .csv file with all the scraped files, add a debug log file
	# and populate the body of the email to mail it to the admins.
	def send_report(self, reportID=None, files_list=None, debug_output=None):
		fromaddr = "ioperspejimai@gmail.com"
		toaddr   = "delriogjl@gmail.com"
		msg = MIMEMultipart()
		msg['From']    = fromaddr
		msg['To']      = toaddr
		msg['Subject'] = "Boletin BC: reporte extraccion boletin del dia " + reportID
		body = "Reporte de script de extraccion de boletin del poder judicial del estado de Baja California.\n\n"
		msg.attach(MIMEText(body, 'plain'))
		if files_list != None:
			# Create the attachment of the message in text/csv.
			attachment = MIMENonMultipart('text', 'csv', charset='utf-8')
			attachment.add_header('Content-Disposition', 'attachment', filename= reportID + '.csv')
			cs = Charset('utf-8')
			cs.body_encoding = BASE64
			csv_data = ''
			for each in files_list:
				csv_row = []
				for i in each:
					csv_row.append(str(i))
				csv_data = csv_data + (', '.join(['"'+i+'"' for i in csv_row])).encode('utf-8') + '\n'
			attachment.set_payload(csv_data, charset=cs)
			msg.attach(attachment)
		# Create the debug log text file.
		attachment_debug = MIMEText(debug_output)
		attachment_debug.add_header('Content-Disposition', 'attachment', filename='debug_log_' + reportID + '.txt')
		msg.attach(attachment_debug)
		self.send_email(toaddr, msg, True)
