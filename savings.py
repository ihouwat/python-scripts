# ! python
# savings.py - Manipulates Monthly Savings GSheet.

# Usage:
        # savings month <integers OR floats> - to do monthly updates of categories
        # savings envelope <integer OR float> - to update cash value in envelope
        # savings interest <integer or float> - to add interest amount to Trips category
        # savings exp - to enter an expense

from datetime import date
from enum import Enum
from logging import exception
import ezsheets, sys
import pyinputplus as pyip

ss = ezsheets.Spreadsheet('1hW1zMXe943epeu1xdHhV-2H4IToKusYkFrp6N9Z5iyk')
sheet = ss[1]
delimiter = '-'
dateFormat = f'%m{delimiter}%d{delimiter}%Y'
today = date.today()
totalDeposits = 0

# Enum for command line args
class Args(str, Enum):
  MONTH = 'month'
  ENVELOPE = 'envelope'
  INTEREST = 'interest'
  EXPENSE = 'exp'

def isFloat(string):
  try:
    float(string)
    return True
  except ValueError:
    return False

def checkCurrentMonth(d):
  todayMonth = getMonth(str(today.strftime(dateFormat)))
  inputMonth = getMonth(d)
  return todayMonth == inputMonth

def splitDate(str):
  return str.split(delimiter)

def getMonth(str):
  return splitDate(str)

def updateCategoryValue(val, acc):
  global totalDeposits
  totalDeposits += float(acc)
  return float(str(val).replace(',','')) + float(acc)

# Check if you have at least two arguments, second argument is found in the Args enum, and all subsequent arguments are floats
def validateArgs():
  floats = []
  for x in enumerate(list(sys.argv)[2:]):
    floats.append(isFloat(x[1]))
  return len(sys.argv) > 1 and all(floats) and sys.argv[1] in list(Args)

def addInterest():
  totalInterest = 0
  for num in sys.argv[2:]:
    totalInterest += float(num)
  sheet['B4'] = updateCategoryValue(sheet['B4'], totalInterest)
  print(f'Added ${totalInterest} in interest to the {sheet["A4"]} category.\n')


# Program starts here
try:
  if(not validateArgs()):
    raise exception
  command = sys.argv[1]

  # Update monthly values
  if(command == Args.MONTH.value):
    lastMonth = sheet['B8']
    updatedThisMonth = checkCurrentMonth(lastMonth)

    # CHANGE THIS LATER
    if(updatedThisMonth):
      print(f'You already have updated monthly savings for {today.strftime("%B")}.')
    else:
      # update values for each category
      for i in range(2,6):
        row = [x for x in sheet.getRow(i) if x]
        category, oldValue, accumulator = row[0], row[1], row[2]
        newValue = updateCategoryValue(oldValue, accumulator)
        sheet[f'B{i}'] = newValue
        print(f'{category}:\n Old Value: {oldValue}\n Monthly Deposit: {accumulator}\n New Value: {"{:,}".format(newValue)}\n')
      
      # add monthly interest to Trips value
      if(sys.argv[2:]):
        addInterest()
      
      # print totals
      print(f'Old Total: {sheet["B6"]}')
      sheet.refresh()
      print(f'New Total: {sheet["B6"]}')
      print(f'Total Deposited: {totalDeposits}')
      
      
      
      
      
      
      # update date
      # sheet['B8'] = today.strftime(dateFormat)
  
  # Update envelope values
  elif(command == Args.ENVELOPE.value):
    try:
      if(len(sys.argv) == 2):
        raise exception

      oldVal = float(str(sheet["B9"]).replace(',',''))
      newVal = oldVal - float(sys.argv[2])
      print(f'Old envelope value: {oldVal}')
      sheet["B9"] = newVal
      print(f'New envelope value: {sheet["B9"]}')
    except:
      print('Include a second arg of type float')

  # Add interest to Trips category
  elif(command == Args.INTEREST.value):
    print(f'{sheet["A4"]} old value: {sheet["B4"]}\n')
    addInterest()
    print(f'{sheet["A4"]} new value: {sheet["B4"]}\n')
    
  elif(command == Args.EXPENSE.value):
    rows = [x for x in ss[2].getRows() if x[0]]
    print(len(rows))
    # categories = [x for x in sheet.getColumn(1) if x][1:5]
    # while(True):
    #   item = pyip.inputStr("Enter item: ")
    #   cost = pyip.inputNum("Enter dollar value: ")
    #   category = pyip.inputMenu(categories, numbered=True)
    #   dateEntered = pyip.inputDate(prompt=f"Enter the date of the expense in {dateFormat} format: ", formats=[dateFormat])
    #   formattedDate = str(dateEntered.strftime(dateFormat))
    #   note = pyip.inputStr("Enter notes to add to expense: ")
    #   confirmation = pyip.inputYesNo(f"Confirm with Yes/No if you want to add:\n {item}\n cost: ${cost}\n category: {category}\n date: {formattedDate}\n notes: {note}\n")
    #   if(confirmation == 'no'):
    #     print("You entered 'no'. Quitting the program.")
    #     break
    #   else:
    #     print(sheet)
      
except:
  print(f"""\nEnter a valid command:
  savings {Args.MONTH.value} <optional integers OR floats> - to do monthly updates of categories
  savings {Args.ENVELOPE.value} <integer OR float> - to update cash value in envelope
  savings {Args.INTEREST.value} <optional integer or float> - to add interest amount to Trips category
  savings {Args.EXPENSE.value} - to enter an expense""")