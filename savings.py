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
totalsSheet = ss[0]
expensesSheet = ss[1]

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
  HELP = 'help'
  
availableCommands = (f"""\nEnter a valid command:
  savings {Args.HELP.value} - to view a list of available commands
  savings {Args.MONTH.value} <optional integers OR floats> - to do monthly updates of categories
  savings {Args.ENVELOPE.value} <integer OR float> - to update cash value in envelope
  savings {Args.INTEREST.value} <optional integer or float> - to add interest amount to Trips category
  savings {Args.EXPENSE.value} - to enter an expense""")

def isFloat(string):
  try:
    float(string)
    return True
  except ValueError:
    return False
  
def cellStringToFloat(num):
  return float(str(num).replace(',',''))

def isCurrentMonth(d):
  todayMonth = getMonth(str(today.strftime(dateFormat)))
  inputMonth = getMonth(d)
  return todayMonth == inputMonth

def monthsSinceLastUpdate(d):
  monthDifferential = 0
  formattedToday = splitDate(str(today.strftime(dateFormat)))
  formattedLast = splitDate(d)
  todayMonth, todayYear = int(formattedToday[0]), int(formattedToday[2])
  formerMonth, lastYear = int(formattedLast[0]), int(formattedLast[2])
  
  if(todayYear > lastYear):
    monthDifferential = 12 - formerMonth + todayMonth
  elif(todayYear == lastYear):
    monthDifferential = 2 - formerMonth
  
  return monthDifferential

def splitDate(str):
  return str.split(delimiter)

def getMonth(str):
  return splitDate(str)

def updateCategoryValue(val, acc):
  global totalDeposits
  totalDeposits += float(acc)
  return cellStringToFloat(val) + float(acc)

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
  totalsSheet['B4'] = updateCategoryValue(totalsSheet['B4'], totalInterest)
  print(f'Added ${totalInterest} in interest to the {totalsSheet["A4"]} category.\n')


# Program starts here
try:
  if(not validateArgs()):
    raise exception
  command = sys.argv[1]
  
  # List commands for user
  if(command == Args.HELP.value):
    print(availableCommands)

  # Update monthly values
  if(command == Args.MONTH.value):
    dateUpdated = totalsSheet['B8']

    if(isCurrentMonth(dateUpdated)):
      print(f'You already have updated monthly savings for {today.strftime("%B")}.')
    else:
      numberOfMonths = monthsSinceLastUpdate(dateUpdated)
      if(numberOfMonths > 1):
        confirmation = pyip.inputYesNo(f'It has been {numberOfMonths} since your last update. Do you want to make the update?')
        if(confirmation == 'no'):
          sys.exit()
      
      # update values for each category
      for j in range(numberOfMonths):
        for i in range(2,6):
          row = [x for x in totalsSheet.getRow(i) if x]
          category, oldValue, accumulator = row[0], row[1], row[2]
          newValue = updateCategoryValue(oldValue, accumulator)
          totalsSheet[f'B{i}'] = newValue
          print(f'{category}:\n Old Value: {oldValue}\n Monthly Deposit: {accumulator}\n New Value: {"{:,}".format(newValue)}\n')
      
      # add monthly interest to Trips value
      if(sys.argv[2:]):
        addInterest()
      
      # print totals
      print(f'Old Total: {totalsSheet["B6"]}')
      totalsSheet.refresh()
      print(f'New Total: {totalsSheet["B6"]}')
      print(f'Total Deposited: {totalDeposits}')
      
      # update date
      totalsSheet['B8'] = today.strftime(dateFormat)
  
  # Update envelope values
  elif(command == Args.ENVELOPE.value):
    try:
      if(len(sys.argv) == 2):
        raise exception

      oldVal = cellStringToFloat(totalsSheet["B9"])
      newVal = oldVal - float(sys.argv[2])
      print(f'Old envelope value: {oldVal}')
      totalsSheet["B9"] = newVal
      print(f'New envelope value: {totalsSheet["B9"]}')
    except:
      print('Include a second arg of type float')

  # Add interest to Trips category
  elif(command == Args.INTEREST.value):
    print(f'{totalsSheet["A4"]} old value: {totalsSheet["B4"]}\n')
    addInterest()
    print(f'{totalsSheet["A4"]} new value: {totalsSheet["B4"]}\n')

  # Add an expense to the Expenses sheet
  elif(command == Args.EXPENSE.value):
    rows = [x for x in expensesSheet.getRows() if x[0]]
    categories = [x for x in totalsSheet.getColumn(1) if x][1:5]

    # get user input
    while(True):
      item = pyip.inputStr("Enter item: ")
      cost = pyip.inputNum("Enter dollar value: ")
      category = pyip.inputMenu(categories, numbered=True)
      dateEntered = pyip.inputDate(prompt=f"Enter the date of the expense in {dateFormat} format: ", formats=[dateFormat])
      note = pyip.inputStr("Enter notes to add to expense: ")
      confirmation = pyip.inputYesNo(f"Confirm with Yes/No if you want to add:\n Item: {item}\n Cost: ${cost}\n Category: {category}\n Date: {str(dateEntered.strftime(dateFormat))}\n Note: {note}\n")

      if(confirmation == 'no'):
        print("You entered 'no'. Quitting the program.")
        break

      else:
        categoryCell = f'B{categories.index(category)+2}'
        oldVal = totalsSheet[categoryCell]
        newVal = cellStringToFloat(totalsSheet[categoryCell]) - cost
        try:
          if(newVal < 0):
            raise exception
          else:
            # Add expense to sheet
            expensesSheet.updateRow(len(rows) + 1, [str(item), str(cost), str(dateEntered), str(category), str(note)])
            # Subtract expense from Totals sheet
            totalsSheet[categoryCell] = newVal
            print(f'Category, {category} was successfully updated.\n Old value: {oldVal}\n New value: {newVal}')
            updatedRows = [x for x in expensesSheet.getRows() if x[0]]
            print('Updated Expenses spreadsheet:')
            for i in updatedRows:
              print(i[:5])
        except:
          print('The updated category can not be less than 0.')
        break

except:
  print('\nCould not complete the operation.', availableCommands)