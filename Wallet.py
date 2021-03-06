#!/usr/bin/env python3
##########################################
# Duino-Coin GUI Wallet (v1.7)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################

from tkinter import Tk, Label, Frame, Entry, StringVar, IntVar, Button, PhotoImage, Listbox, Scrollbar, Checkbutton, Toplevel
from tkinter.font import Font
from tkinter import LEFT, BOTH, RIGHT, END, N, E, S, W
from webbrowser import open_new_tab
from urllib.request import urlopen, urlretrieve
from pathlib import Path
import socket, sys
from threading import Timer
from PIL import Image, ImageTk
from time import sleep
from os import _exit, mkdir, execl
import datetime
from tkinter import messagebox
from base64 import b64encode, b64decode
from requests import get
from json import loads
from configparser import ConfigParser
import json
config = ConfigParser()
resources = "res/"
backgroundColor = "#FEEEDA"
foregroundColor = "#212121"
min_trans_difference = 0.000000001 # Minimum transaction amount to be saved

import sqlite3

try:
	mkdir(resources)
except FileExistsError:
	pass

with sqlite3.connect(f"{resources}/wallet.db") as con:
	cur = con.cursor()
	cur.execute('''CREATE TABLE IF NOT EXISTS Transactions(Transaction_Date TEXT, amount REAL)''')
	cur.execute('''CREATE TABLE IF NOT EXISTS UserData(username TEXT, password TEXT)''')


with urlopen("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt") as content:
	content = content.read().decode().splitlines()
	pool_address = content[0]
	pool_port = content[1]

def GetDucoPrice():
	global ducofiat
	jsonapi = get("http://51.15.127.80/api.json", data = None)
	if jsonapi.status_code == 200:
		content = jsonapi.content.decode()
		contentjson = loads(content)
		ducofiat = round(float(contentjson["Duco price"]), 6)
	else:
		ducofiat = .003
	Timer(15, GetDucoPrice).start()
GetDucoPrice()

class LoginFrame(Frame):
	def __init__(self, master):
		""" init login frame """
		super().__init__(master)

		master.title("Login")
		master.resizable(False, False)
		#master.geometry("220x350")
		master.configure(background = backgroundColor)
		self.configure(background = backgroundColor)

		textFont2 = Font(size=12,weight="bold")
		# textFont3 = Font(size=14,weight="bold")
		textFont = Font(size=12,weight="normal")

		self.duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
		self.duco.image = self.duco
		self.ducoLabel = Label(self, background = "#ff7f50",image = self.duco)
		self.ducoLabel2 = Label(self,
			background = "#ff7f50",
			foreground="#FAFAFA",
			text="Welcome to the\nDuino-Coin\nTkinter GUI Wallet",font=textFont2)
		self.spacer = Label(self, background = backgroundColor)

		self.label_username = Label(self, text="USERNAME",
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)
		self.label_password = Label(self, text="PASSWORD",
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)

		self.entry_username = Entry(self,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont)
		self.entry_password = Entry(self, show="*",
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont)


		self.ducoLabel.grid(row=0, sticky="nswe", pady=(5,0), padx=(5))
		self.ducoLabel2.grid(row=1, sticky="nswe", padx=(5))
		self.spacer.grid(row=3, sticky="nswe", padx=(5))
		self.label_username.grid(row=4, sticky=W, pady=(5))
		self.entry_username.grid(row=5, sticky=N, padx=(5))
		self.label_password.grid(row=6, sticky=W, pady=(5))
		self.entry_password.grid(row=7, sticky=N, pady=(5))

		self.var = IntVar()
		self.checkbox = Checkbutton(self, text="Keep me logged in", variable=self.var,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont, borderwidth="0", highlightthickness="0")
		self.checkbox.grid(columnspan=2)

		self.logbtn = Button(self, text="LOGIN", command=self._login_btn_clicked,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)
		self.logbtn.grid(columnspan=2,sticky="nswe", padx=(5), pady=(0, 3))

		self.regbtn = Button(self, text="REGISTER", command=self._register_btn_clicked,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)
		self.regbtn.grid(columnspan=2,sticky="nswe", padx=(5), pady=(0, 5))

		self.pack()

	def _login_btn_clicked(self):
		global username, password
		username = self.entry_username.get()
		password = self.entry_password.get()
		keeplogedin = self.var.get()

		if username and password:
			soc = socket.socket()
			soc.connect((pool_address, int(pool_port)))
			soc.recv(3)
			soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
			response = soc.recv(64).decode("utf8")
			response = response.split(",")

			if response[0] == "OK":
				if keeplogedin >= 1:
					passwordEnc = b64encode(bytes(password, encoding="utf8"))
					with sqlite3.connect(f"{resources}/wallet.db") as con:
						cur = con.cursor()
						cur.execute('''INSERT INTO UserData(username, password) VALUES(?, ?)''',(username, passwordEnc))
						con.commit()
				root.destroy()
			else:
				messagebox.showerror(title="Error loging-in", message=response[1])
		else:
			messagebox.showerror(title="Error loging-in", message="Fill in the blanks first")

	def _registerprotocol(self):
		emailS = email.get()
		usernameS = username.get()
		passwordS = password.get()
		confpasswordS = confpassword.get()

		if emailS and usernameS and passwordS and confpasswordS:
			if passwordS == confpasswordS:
				soc = socket.socket()
				soc.connect((pool_address, int(pool_port)))
				soc.recv(3)
				soc.send(bytes(f"REGI,{str(usernameS)},{str(passwordS)},{str(emailS)}", encoding="utf8"))
				response = soc.recv(128).decode("utf8")
				response = response.split(",")

				if response[0] == "OK":
					messagebox.showinfo(title="Registration successfull",
						message="New user has been registered sucessfully. You can now login")
					register.destroy()
					execl(sys.executable, sys.executable, *sys.argv)
				else:
					messagebox.showerror(title="Error registering user",
						message=response[1])
			else:
				messagebox.showerror(title="Error registering user",
					message="Passwords don't match")
		else:
			messagebox.showerror(title="Error registering user",
				message="Fill in the blanks first")

	def _register_btn_clicked(self):
		global username, password, confpassword, email, register
		root.destroy()
		register = Tk()
		register.title("Register")
		register.resizable(False, False)
		#register.geometry("220x350")
		register.configure(background = backgroundColor)

		textFont2 = Font(register, size=12,weight="bold")
		# textFont3 = Font(register, size=14,weight="bold")
		textFont = Font(register, size=12,weight="normal")

		duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
		duco.image = duco
		ducoLabel = Label(register, background = "#ff7f50", image = duco)
		ducoLabel2 = Label(register,
						background = "#ff7f50",
						foreground="#FAFAFA",
						text="Register on network",font=textFont2)
		ducoLabel.grid(row=0, padx=5, pady=(5,0), sticky="nswe")
		ducoLabel2.grid(row=1, padx=5, sticky="nswe")
		Label(register, background = backgroundColor).grid(row=2, padx=5)

		Label(register, text="USERNAME",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=3, sticky=W)
		username = Entry(register, background=backgroundColor,
						foreground=foregroundColor,
						font=textFont)
		username.grid(row=4, padx=5)

		Label(register, text="PASSWORD",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=5, sticky=W)
		password = Entry(register, background=backgroundColor, show="*",
						foreground=foregroundColor,
						font=textFont)
		password.grid(row=6, padx=5)

		Label(register, text="CONFIRM PASSWORD",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=7, sticky=W)
		confpassword = Entry(register, background=backgroundColor, show="*",
						foreground=foregroundColor,
						font=textFont)
		confpassword.grid(row=8, padx=5)

		Label(register, text="E-MAIL",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=9, sticky=W)
		email = Entry(register, background=backgroundColor,
						foreground=foregroundColor,
						font=textFont)
		email.grid(row=10, padx=5)

		self.logbtn = Button(register, text="REGISTER", command=self._registerprotocol,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)
		self.logbtn.grid(columnspan=2, sticky="nswe", padx=(5, 5), pady=(5,5))

if not Path(resources + "duco.png").is_file():
	urlretrieve('https://i.imgur.com/GXXsMAC.png', resources + 'duco.png')
if not Path(resources + "calculator.png").is_file():
	urlretrieve('https://i.imgur.com/j0CnOkc.png', resources + 'calculator.png')
if not Path(resources + "exchange.png").is_file():
	urlretrieve('https://i.imgur.com/bBnX0kn.png', resources + 'exchange.png')
if not Path(resources + "discord.png").is_file():
	urlretrieve('https://i.imgur.com/3iTh8XD.png', resources + 'discord.png')
if not Path(resources + "github.png").is_file():
	urlretrieve('https://i.imgur.com/d8YEl7k.png', resources + 'github.png')
if not Path(resources + "send.png").is_file():
	urlretrieve('https://i.imgur.com/OvufpeF.png', resources + 'send.png')
if not Path(resources + "send2.png").is_file():
	urlretrieve('https://i.imgur.com/QamfUhf.png', resources + 'send2.png')
if not Path(resources + "settings.png").is_file():
	urlretrieve('https://i.imgur.com/vQitW9M.png', resources + 'settings.png')
if not Path(resources + "transactions.png").is_file():
	urlretrieve('https://i.imgur.com/lR8ZCwA.png', resources + 'transactions.png')
if not Path(resources + "stats.png").is_file():
	urlretrieve('https://icons-for-free.com/iconfiles/png/512/STATISTICS-131994911363180250.png', resources + 'stats.png')

with sqlite3.connect(f"{resources}/wallet.db") as con:
	cur = con.cursor()
	cur.execute("SELECT COUNT(username) FROM UserData")
	userdata_count = cur.fetchall()[0][0]
if userdata_count != 1:
	root = Tk()
	lf = LoginFrame(root)
	root.mainloop()
else:
	with sqlite3.connect(f"{resources}/wallet.db") as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM UserData")
		userdata_query = cur.fetchone()
		username = userdata_query[0]
		passwordEnc = (userdata_query[1]).decode("utf-8")
		password = b64decode(passwordEnc).decode("utf8")

def openWebsite(handler):
	open_new_tab("https://duinocoin.com")

def openGitHub(handler):
	open_new_tab("https://github.com/revoxhere/duino-coin")

def openExchange(handler):
	open_new_tab("https://revoxhere.github.io/duco-exchange/")

def openDiscord(handler):
	open_new_tab("https://discord.com/invite/kvBkccy")

def openTransactions(handler):
	transactionsWindow = Toplevel()
	transactionsWindow.geometry("420x420")
	transactionsWindow.resizable(False, False)
	transactionsWindow.title("Duino-Coin Wallet - Transactions")
	transactionsWindow.configure(background = backgroundColor)
	transactionsWindow.transient([root])

	# textFont2 = Font(transactionsWindow, size=12,weight="bold")
	textFont3 = Font(transactionsWindow, size=14,weight="bold")
	textFont = Font(transactionsWindow, size=12,weight="normal")

	Label(transactionsWindow,
		text="LOCAL TRANSACTIONS LIST",
		font=textFont3,
		background=backgroundColor,
		foreground=foregroundColor).pack()
	Label(transactionsWindow,
		text="This feature will be improved in the near future",
		font=textFont,
		background=backgroundColor,
		foreground=foregroundColor).pack()

	listbox = Listbox(transactionsWindow)
	listbox.pack(side = LEFT, fill = BOTH, expand=1)
	scrollbar = Scrollbar(transactionsWindow)
	scrollbar.pack(side = RIGHT, fill = BOTH)

	with sqlite3.connect(f"{resources}/wallet.db") as con:
		cur = con.cursor()
		cur.execute("SELECT rowid,* FROM Transactions ORDER BY rowid DESC")
		Transactions = cur.fetchall()
	# transactionstext_format = ''
	for i, row in enumerate(Transactions, start=1):
		listbox.insert(END, f"{str(row[1])}  {row[2]} DUCO\n")


	listbox.config(highlightcolor = backgroundColor,
				selectbackground = "#f39c12", bd = 0,
				yscrollcommand = scrollbar.set,
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont)
	scrollbar.config(command = listbox.yview, background = "#7bed9f")


def currencyConvert():
	fromcurrency = fromCurrencyInput.get(fromCurrencyInput.curselection())
	tocurrency = toCurrencyInput.get(toCurrencyInput.curselection())
	amount = amountInput.get()

	try:
		if fromcurrency != "DUCO":
			currencyapi = get("https://api.exchangeratesapi.io/latest?base="+str(fromcurrency), data=None)
			exchangerates = loads(currencyapi.content.decode())
		else:
			currencyapi = get("https://api.exchangeratesapi.io/latest?base=USD", data=None)
			exchangerates = loads(currencyapi.content.decode())

		if currencyapi.status_code == 200: #Check for reponse
			if fromcurrency == "DUCO" and tocurrency != "DUCO":
				exchangerates = loads(currencyapi.content.decode())
				result = str(round(float(amount) * float(ducofiat) * float(exchangerates["rates"][tocurrency]), 6)) + " " + str(tocurrency)
			else:
				if tocurrency == "DUCO":
					currencyapisss = get("https://api.exchangeratesapi.io/latest?symbols="+str(fromcurrency)+",USD", data=None)
					if currencyapi.status_code == 200: #Check for reponse
						exchangeratesss = loads(currencyapisss.content.decode())
						result = str(round(float(amount) * float(1/ducofiat) / float(exchangeratesss["rates"][fromcurrency]), 6)) + " " + str(tocurrency)
				else:
					result = str(round(float(amount) * float(exchangerates["rates"][tocurrency]), 6)) + " " + str(tocurrency)
	except:
		result = "Incorrect calculation"
	result = "RESULT: " + result
	conversionresulttext.set(str(result))
	calculatorWindow.update()

def openCalculator(handler):
	global conversionresulttext, fromCurrencyInput, toCurrencyInput, amountInput, calculatorWindow

	currencyapi = get("https://api.exchangeratesapi.io/latest", data=None)
	if currencyapi.status_code == 200: #Check for reponse
		exchangerates = loads(currencyapi.content.decode())
		exchangerates["rates"]["DUCO"] = float(ducofiat)

	calculatorWindow = Toplevel()
	#calculatorWindow.geometry("420x420")
	calculatorWindow.resizable(False, False)
	calculatorWindow.title("Duino-Coin Wallet - Calculator")
	calculatorWindow.configure(background = backgroundColor)
	calculatorWindow.transient([root])

	textFont2 = Font(calculatorWindow, size=12,weight="bold")
	textFont3 = Font(calculatorWindow, size=14,weight="bold")
	textFont = Font(calculatorWindow, size=12,weight="normal")

	Label(calculatorWindow, text="CURRENCY CONVERTER",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont3).grid(row=0, column=0)

	Label(calculatorWindow, text="FROM",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont2).grid(row=1, column=0)

	fromCurrencyInput = Listbox(calculatorWindow,
								exportselection=False,
								background = backgroundColor,
								foreground = foregroundColor,
								selectbackground = "#7bed9f",
								border="0", font=textFont,
								width="20", height="13")
	fromCurrencyInput.grid(row=2, column=0)
	i=0
	for currency in exchangerates["rates"]:
		fromCurrencyInput.insert(i, currency)
		i = i+1

	Label(calculatorWindow, text="TO",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont2).grid(row=1, column=1)

	toCurrencyInput = Listbox(calculatorWindow,
								exportselection=False,
								foreground = foregroundColor,
								background = backgroundColor,
								selectbackground = "#7bed9f",
								border="0", font=textFont,
								width="20", height="13")
	toCurrencyInput.grid(row=2, column=1)
	i=0
	for currency in exchangerates["rates"]:
		toCurrencyInput.insert(i, currency)
		i = i+1

	toCurrencyInput.select_set(0)
	toCurrencyInput.event_generate("<<ListboxSelect>>")
	fromCurrencyInput.select_set(32)
	fromCurrencyInput.event_generate("<<ListboxSelect>>")

	Label(calculatorWindow, text="AMOUNT",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont2).grid(row=3, column=0)

	def clear_ccamount_placeholder(self):
			amountInput.delete("0", "100")

	amountInput = Entry(calculatorWindow,
						background = "#7bed9f", foreground=foregroundColor,
						border="0", font=textFont,
						width="20")
	amountInput.grid(row=4, column=0)
	amountInput.insert("0", str(getBalance()))
	amountInput.bind("<FocusIn>", clear_ccamount_placeholder)

	Button(calculatorWindow, text="Convert",
			background = "#FEEEDA", foreground=foregroundColor,
			command=currencyConvert, width="22").grid(row=3, column=1, pady=(5, 0))

	conversionresulttext = StringVar(calculatorWindow)
	conversionresulttext.set("RESULT: 0.0")
	conversionresultLabel = Label(calculatorWindow,
								textvariable=conversionresulttext,
								background = backgroundColor,
								foreground = foregroundColor,
								font = textFont2)
	conversionresultLabel.grid(row=4, column=1)

	Label(calculatorWindow, text=" ",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont2).grid(row=5, column=0)

	calculatorWindow.mainloop()

def openStats(handler):
	statsApi = get("https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json", data=None)
	if statsApi.status_code == 200: #Check for reponse
		statsApi = (statsApi.json())
		print(statsApi)

	statsWindow = Toplevel()
	statsWindow.resizable(False, False)
	statsWindow.title("Duino-Coin Wallet - Stats")
	statsWindow.configure(background = backgroundColor)
	statsWindow.transient([root])

	textFont3 = Font(statsWindow, size=14,weight="bold")
	textFont = Font(statsWindow, size=12,weight="normal")

	Label(statsWindow, text="Duco Statistics",
		background = backgroundColor,
		foreground = foregroundColor,
		font = textFont3).grid(row=0, column=0)

	i = 3
	i2 = 3
	for key in statsApi.keys():
		if str(key) == 'Active workers' or str(key) == 'Top 10 richest miners' or str(key) == 'Total supply' or str(key) == 'Full last block hash' or str(key) == 'GitHub API file update count' or str(key) == 'Diff increases per':
			pass
		else:
			if len(statsApi.get(str(key))) > 8:
				Label(statsWindow, text=f"{key}: {statsApi.get(str(key))}",
				background = backgroundColor,
				foreground = foregroundColor,
				font = textFont).grid(row=i2, column=1, sticky=W)
				i2 += 1
			else:
				Label(statsWindow, text=f"{key}: {statsApi.get(str(key))}",
				background = backgroundColor,
				foreground = foregroundColor,
				font = textFont).grid(row=i, column=0, sticky=W)
				i += 1

	Active_workers_listbox = Listbox(statsWindow,
								exportselection=False,
								background = backgroundColor,
								foreground = foregroundColor,
								selectbackground = "#7bed9f",
								border="0", font=textFont,
								width="20", height="13")
	Active_workers_listbox.grid(row=1, column=0, sticky=W)
	i=0
	for worker in (statsApi['Active workers']).split(', '):
		Active_workers_listbox.insert(i, worker)
		i = i+1

	Active_workers_listbox.select_set(32)
	Active_workers_listbox.event_generate("<<ListboxSelect>>")

	Top_10_listbox = Listbox(statsWindow,
								exportselection=False,
								background = backgroundColor,
								foreground = foregroundColor,
								selectbackground = "#7bed9f",
								border="0", font=textFont,
								width="33", height="13")
	Top_10_listbox.grid(row=1, column=1, sticky=W)
	i=0
	for rich in (statsApi['Top 10 richest miners']).split(', '):
		Top_10_listbox.insert(i, rich)
		i = i+1

	Top_10_listbox.select_set(32)
	Top_10_listbox.event_generate("<<ListboxSelect>>")

	statsWindow.mainloop()

def openSettings(handler):
	def _logout():
		try:
			with sqlite3.connect(f"{resources}/wallet.db") as con:
				cur = con.cursor()
				cur.execute('DELETE FROM UserData')
				con.commit()
		except Exception as e:
			print(e)
		# remove(resources + "userdata.bin")
		try:
			execl(sys.executable, sys.executable, *sys.argv)
		except Exception as e:
			print(e)

	def _cleartrs():
		# open(resources + "transactions.bin", "w+")
		with sqlite3.connect(f"{resources}/wallet.db") as con:
			cur = con.cursor()
			cur.execute('DELETE FROM transactions')
			con.commit()

	def _chgpass():
		def _changepassprotocol():
			oldpasswordS = oldpassword.get()
			newpasswordS = newpassword.get()
			confpasswordS = confpassword.get()

			if oldpasswordS != newpasswordS:
				if oldpasswordS and newpasswordS and confpasswordS:
					if newpasswordS == confpasswordS:
						soc = socket.socket()
						soc.connect((pool_address, int(pool_port)))
						soc.recv(3)
						soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
						soc.recv(2)
						soc.send(bytes(f"CHGP,{str(oldpasswordS)},{str(newpasswordS)}", encoding="utf8"))
						response = soc.recv(128).decode("utf8")
						soc.close()

						if not "Success" in response:
							messagebox.showerror(title="Error changing password", message=response)
						else:
							messagebox.showinfo(title="Password changed", message=response)
							try:
								# remove(resources + "userdata.bin")
								try:
									with sqlite3.connect(f"{resources}/wallet.db") as con:
										cur = con.cursor()
										cur.execute('DELETE FROM UserData')
										con.commit()
								except Exception as e:
									print(e)
							except FileNotFoundError:
								pass
							execl(sys.executable, sys.executable, *sys.argv)
					else:
						messagebox.showerror(title="Error changing password",
							message="New passwords don't match")
				else:
					messagebox.showerror(title="Error changing password",
						message="Fill in the blanks first")
			else:
				messagebox.showerror(title="Error changing password",
					message="New password is the same as the old one")

		settingsWindow.destroy()
		changepassWindow = Toplevel()
		changepassWindow.title("Change password")
		changepassWindow.resizable(False, False)
		changepassWindow.configure(background = backgroundColor)
		changepassWindow.transient([root])


		textFont2 = Font(changepassWindow, size=12,weight="bold")
		# textFont3 = Font(changepassWindow, size=14,weight="bold")
		textFont = Font(changepassWindow, size=12,weight="normal")

		Label(changepassWindow, text="OLD PASSWORD",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=0, sticky=W)
		oldpassword = Entry(changepassWindow, background=backgroundColor, show="*",
						foreground=foregroundColor,
						font=textFont)
		oldpassword.grid(row=1, sticky="nswe", padx=5)

		Label(changepassWindow, text="NEW PASSWORD",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=2, sticky=W)
		newpassword = Entry(changepassWindow, background=backgroundColor, show="*",
						foreground=foregroundColor,
						font=textFont)
		newpassword.grid(row=3, sticky="nswe", padx=5)

		Label(changepassWindow, text="CONFIRM NEW PASSWORD",
				background=backgroundColor,
				foreground=foregroundColor,
				font=textFont2).grid(row=4, sticky=W)
		confpassword = Entry(changepassWindow, background=backgroundColor, show="*",
						foreground=foregroundColor,
						font=textFont)
		confpassword.grid(row=5, sticky="nswe", padx=5)

		chgpbtn = Button(changepassWindow, text="CHANGE PASSWORD", command=_changepassprotocol,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont2)
		chgpbtn.grid(columnspan=2, sticky="nswe", pady=(5,5), padx=(5,5))

	settingsWindow = Toplevel()
	settingsWindow.resizable(False, False)
	settingsWindow.title("Duino-Coin Wallet - Settings")
	settingsWindow.configure(background = backgroundColor)
	settingsWindow.transient([root])

	textFont = Font(settingsWindow,  size=12, weight="normal")

	logoutbtn = Button(settingsWindow, text="LOGOUT", command=_logout,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont)
	logoutbtn.grid(row=0, columnspan=1,sticky="nswe")

	chgpassbtn = Button(settingsWindow, text="CHANGE PASSWORD", command=_chgpass,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont)
	chgpassbtn.grid(row=1, columnspan=1,sticky="nswe")

	cleartransbtn = Button(settingsWindow, text="CLEAR TRANSACTIONS", command=_cleartrs,
										background=backgroundColor,
										foreground=foregroundColor,
										font=textFont)
	cleartransbtn.grid(row=2, columnspan=1,sticky="nswe")

	infolbl = Label(settingsWindow,
					text="More options will come in the future",
					background=backgroundColor,
					foreground=foregroundColor,
					font=textFont)
	infolbl.grid(row=3)

oldbalance = 0
balance = 0
unpaid_balance = 0
def getBalance():
	global oldbalance, balance, unpaid_balance

	try:
		soc = socket.socket()
		soc.connect((pool_address, int(pool_port)))
		soc.recv(3)
		soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
		_ = soc.recv(2)
		soc.send(bytes("BALA", encoding="utf8"))
		oldbalance = balance
		balance = soc.recv(1024).decode()
		soc.close()
	except ConnectionResetError:
		getBalance()

	try:
		if oldbalance != balance:
			difference = (float(balance) - float(oldbalance))
			dif_with_unpaid = (float(balance) - float(oldbalance)) + unpaid_balance
			if float(balance) != float(difference):
				if dif_with_unpaid >= min_trans_difference or dif_with_unpaid < 0:
					now = datetime.datetime.now()
					difference = (round(dif_with_unpaid, 12))
					with sqlite3.connect(f"{resources}/wallet.db") as con:
						cur = con.cursor()
						cur.execute('''INSERT INTO Transactions(Transaction_Date, amount) VALUES(?, ?)''',(now.strftime("%d %b %Y %H:%M:%S"), float(difference)))
						con.commit()
						unpaid_balance = 0
				else:
					unpaid_balance += (float(balance) - float(oldbalance))
	except Exception as e:
		print(e)

	return round(float(balance), 8)

profitCheck = 0
def updateBalanceLabel():
	global profit_array, profitCheck
	try:
		balancetext.set(str(getBalance()))
		balanceusdtext.set("$"+str(round(getBalance()*ducofiat, 6)))

		# with open(resources + "transactions.bin", "r") as transactionsFile:
		# 	transactionsFileContent = transactionsFile.read().splitlines()
		# try:
		# 	transactionstext.set(transactionsFileContent[0] +"\n"
		# 						+ transactionsFileContent[1] +"\n"
		# 						+ transactionsFileContent[2] +"\n"
		# 						+ transactionsFileContent[3] +"\n"
		# 						+ transactionsFileContent[4] +"\n"
		# 						+ transactionsFileContent[5])
		# except IndexError:
		# 	transactionstext.set("No local transactions yet")

		with sqlite3.connect(f"{resources}/wallet.db") as con:
			cur = con.cursor()
			cur.execute("SELECT rowid,* FROM Transactions ORDER BY rowid DESC")
			Transactions = cur.fetchall()
		try:
			transactionstext_format = ''
			for i, row in enumerate(Transactions, start=1):
				transactionstext_format += f"{str(row[1])}	{row[2]} DUCO\n"
				if i == 6:
					break
			transactionstext.set(transactionstext_format)
		except IndexError:
			transactionstext.set("No local transactions yet")

		if profit_array[2] != 0:
			sessionprofittext.set("SESSION: " + str(profit_array[0]) + " ᕲ")
			minuteprofittext.set("≈" + str(profit_array[1]) + " ᕲ/MINUTE")
			hourlyprofittext.set("≈" + str(profit_array[2]) + " ᕲ/HOUR")
			dailyprofittext.set("≈" + str(profit_array[3]) + " ᕲ/DAY ("+str(round(profit_array[3]*ducofiat, 4))+" $)")
		else:
			if profitCheck > 5:
				sessionprofittext.set("Launch your miners")
				minuteprofittext.set("first to see estimated profit.")
				hourlyprofittext.set("")
				dailyprofittext.set("")
			profitCheck += 1
	except Exception as e:
		print(e)
		_exit(0)
	Timer(.5, updateBalanceLabel).start()

def calculateProfit(start_bal):
	try: # Thanks Bilaboz for the code!
		global curr_bal, profit_array

		curr_bal = getBalance()
		prev_bal = curr_bal
		session = curr_bal - start_bal
		tensec = curr_bal - prev_bal
		minute = tensec * 6
		hourly = minute * 60
		daily = hourly * 12

		if tensec >= 0:
			profit_array = [round(session, 8), round(minute,6), round(hourly,4), round(daily,2)]
	except:
		_exit(0)
	Timer(10, calculateProfit, [start_bal]).start()


def sendFunds(handler):
	recipientStr = recipient.get()
	amountStr = amount.get()

	soc = socket.socket()
	soc.connect((pool_address, int(pool_port)))
	soc.recv(3)

	soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
	response = soc.recv(2)
	soc.send(bytes(f"SEND,-,{str(recipientStr)},{str(amountStr)}", encoding="utf8"))

	response = soc.recv(128).decode()
	soc.close()

	# transactionstatus.set(response)
	root.update()
	sleep(3.5)
	# transactionstatus.set("")
	root.update()

class Wallet:
	def __init__(self, master):
		global recipient, amount, balancetext
		# global transactionstatus
		global sessionprofittext, minuteprofittext, hourlyprofittext,dailyprofittext
		global balanceusdtext, ducopricetext
		global transactionstext
		global curr_bal, profit_array

		textFont3 = Font(size=12,weight="bold")
		textFont2 = Font(size=22,weight="bold")
		textFont = Font(size=12,weight="normal")
		rsize = Font(size=10)

		self.master = master
		master.geometry("720x420")
		master.resizable(False, False)
		master.title("Duino-Coin Wallet")
		master.configure(background = backgroundColor)

		Label(master, # UP - DOWN
			background="#7bed9f", font=rsize,
			width="10", height="100").place(relx=.0, rely= .0)

		Label(master, # LEFT - RIGHT
			background="#f5cd79", font=rsize,
			width="150", height="4").place(relx=.0, rely= .0)

		Label(master, # SQUARE
			background="#ff7f50", font=rsize,
			width="10", height="4").place(relx=.0, rely= .0)

		balancetext = StringVar()
		balancetext.set("Please wait...")
		balanceLabel = Label(master,
							textvariable=balancetext,
							background="#f5cd79",
							foreground=foregroundColor,
							font=textFont2)
		balanceLabel.place(relx=.15, rely= .07)


		Label(master, text="1 DUCO = $"+str(ducofiat),
			background="#f5cd79",
			foreground=foregroundColor,
			font=textFont).place(relx=.6, rely= .11)

		Label(master, text="BALANCE",
			background="#f5cd79",
			foreground=foregroundColor,
			font=textFont).place(relx=.1525, rely= .0155)

		Label(master, text="FIAT BALANCE",
			background="#f5cd79",
			foreground=foregroundColor,
			font=textFont).place(relx=.6, rely= .015)

		balanceusdtext = StringVar()
		balanceusdtext.set("Please wait...")
		balanceusdLabel = Label(master,
							textvariable=balanceusdtext,
							background="#f5cd79",
							foreground=foregroundColor,
							font=textFont3)
		balanceusdLabel.place(relx=.6, rely= .06)

		duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
		duco.image = duco
		ducoLabel = Label(master, background = "#ff7f50", image = duco)
		ducoLabel.place(relx=.005, rely=.0025)
		ducoLabel.bind("<Button>", openWebsite)

		transactions = ImageTk.PhotoImage(Image.open(resources + "transactions.png"))
		transactions.image = transactions
		transactionsLabel =  Label(master, background = "#7bed9f", image = transactions)
		transactionsLabel.place(relx=.005, rely=.2)
		transactionsLabel.bind("<Button>", openTransactions)

		calculator = ImageTk.PhotoImage(Image.open(resources + "calculator.png"))
		calculator.image = calculator
		calculatorLabel =  Label(master,
							background = "#7bed9f",
							image = calculator)
		calculatorLabel.place(relx=.005, rely=.37)
		calculatorLabel.bind("<Button>", openCalculator)

		original = Image.open(resources + "stats.png")
		resized = original.resize((64, 64),Image.ANTIALIAS)

		stats = ImageTk.PhotoImage(resized)
		stats.image = stats
		statsLabel =  Label(master,
							background = "#7bed9f",
							image = stats)
		statsLabel.place(relx=.005, rely=.53)
		statsLabel.bind("<Button>", openStats)

		settings = ImageTk.PhotoImage(Image.open(resources + "settings.png"))
		settings.image = settings
		settingsLabel =  Label(master,
							background = "#7bed9f",
							image = settings)
		settingsLabel.place(relx=.005, rely=.82)
		settingsLabel.bind("<Button>", openSettings)

		Label(master, text="RECIPIENT",
			font=textFont,
			background=backgroundColor,
			foreground=foregroundColor).place(relx=.15, rely=.2)

		def clear_recipient_placeholder(self):
			recipient.delete("0", "100")

		recipient = Entry(master, background = "#87ebff", foreground=foregroundColor, border="0",font=textFont, width="20")
		recipient.place(relx=.1525, rely= .255)
		recipient.insert("0", "revox")
		recipient.bind("<FocusIn>", clear_recipient_placeholder)

		Label(master, text="AMOUNT",
			font=textFont,
			background=backgroundColor,
			foreground=foregroundColor).place(relx=.15, rely=.32)

		def clear_amount_placeholder(self):
			amount.delete("0", "100")

		amount = Entry(master,background = "#87ebff", foreground=foregroundColor, border="0", font=textFont, width="20")
		amount.place(relx=.1525, rely= .375)
		amount.insert("0", "1.7")
		amount.bind("<FocusIn>", clear_amount_placeholder)

		def changeDucoColor(handler):
			sendLabel.configure(image = send2)
		def changeDucoColor2(handler):
			sendLabel.configure(image = send)

		send = ImageTk.PhotoImage(Image.open(resources + "send.png"))
		send.image = send
		send2 = ImageTk.PhotoImage(Image.open(resources + "send2.png"))
		send2.image = send2
		sendLabel =  Label(master,
							background = "#FEEEDA",
							image = send)
		sendLabel.place(relx=.45, rely=.25)
		sendLabel.bind("<Button-1>", sendFunds)
		sendLabel.bind("<Enter>", changeDucoColor)
		sendLabel.bind("<Leave>", changeDucoColor2)

		# transactionstatus = StringVar()
		# transactionLabel = Label(master, textvariable=transactionstatus,
		# 	font=textFont,
		# 	background=backgroundColor,
		# 	foreground=foregroundColor).place(relx=.15, rely=.435)

		Label(master, text="PROFIT",
			background="#feeeda",
			foreground=foregroundColor,
			font=textFont3).place(relx=.6, rely= .2)

		sessionprofittext = StringVar()
		sessionprofittext.set("Please wait - calculating...")
		sessionProfitLabel = Label(master,
							textvariable=sessionprofittext,
							background="#feeeda",
							foreground=foregroundColor,
							font=textFont)
		sessionProfitLabel.place(relx=.6, rely= .25)

		minuteprofittext = StringVar()
		minuteProfitLabel = Label(master,
							textvariable=minuteprofittext,
							background="#feeeda",
							foreground=foregroundColor,
							font=textFont)
		minuteProfitLabel.place(relx=.6, rely= .3)

		hourlyprofittext = StringVar()
		hourlyProfitLabel = Label(master,
							textvariable=hourlyprofittext,
							background="#feeeda",
							foreground=foregroundColor,
							font=textFont)
		hourlyProfitLabel.place(relx=.6, rely= .35)

		dailyprofittext = StringVar()
		dailyprofittext.set("")
		dailyProfitLabel = Label(master,
							textvariable=dailyprofittext,
							background="#feeeda",
							foreground=foregroundColor,
							font=textFont)
		dailyProfitLabel.place(relx=.6, rely= .4)

		Label(master, text="LOCAL TRANSACTIONS",
					background="#feeeda",
					foreground=foregroundColor,
					font=textFont3).place(relx=.15, rely= .5)

		transactionstext = StringVar()
		transactionstext.set("")
		transactionstextLabel = Label(master,
							textvariable=transactionstext,
							background="#feeeda",
							foreground=foregroundColor,
							font=textFont, justify=LEFT)
		transactionstextLabel.place(relx=.15, rely= .5525)


		github = ImageTk.PhotoImage(Image.open(resources + "github.png"))
		github.image = github
		githubLabel =  Label(master,
							background = "#FEEEDA",
							image = github)
		githubLabel.place(relx=.805, rely=.875)
		githubLabel.bind("<Button-1>", openGitHub)

		exchange = ImageTk.PhotoImage(Image.open(resources + "exchange.png"))
		exchange.image = exchange
		exchangeLabel =  Label(master,
							background = "#FEEEDA",
							image = exchange)
		exchangeLabel.place(relx=.865, rely=.875)
		exchangeLabel.bind("<Button-1>", openExchange)

		discord = ImageTk.PhotoImage(Image.open(resources + "discord.png"))
		discord.image = discord
		discordLabel =  Label(master,
							background = "#FEEEDA",
							image = discord)
		discordLabel.place(relx=.925, rely=.875)
		discordLabel.bind("<Button-1>", openDiscord)

		root.iconphoto(True, PhotoImage(file=resources + "duco.png"))
		start_balance = getBalance()
		curr_bal = start_balance
		calculateProfit(start_balance)
		updateBalanceLabel()

		root.mainloop()

try:
	root = Tk()
	my_gui = Wallet(root)
except ValueError:
	_exit(0)
except NameError:
	_exit(0)
