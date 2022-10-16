import json
import os
import applescript
from dotenv import load_dotenv
import datetime
import traceback

load_dotenv()
TASKS_FILE_LOCATION = os.getenv('TASKS_FILE_LOCATION')
ERROR_IN_TASKS_FILE_LOCATION = os.getenv('ERROR_IN_TASKS_FILE_LOCATION')
ERROR_IN_LISTS_FILE_LOCATION = os.getenv('ERROR_IN_LISTS_FILE_LOCATION')
DEFAULT_REMINDERS_LIST_NAME = os.getenv('DEFAULT_REMINDERS_LIST_NAME')

taskFile = open(TASKS_FILE_LOCATION)
errorInTasksFile = open(ERROR_IN_TASKS_FILE_LOCATION, 'a+')
errorInListsFile = open(ERROR_IN_LISTS_FILE_LOCATION, 'a+')

tasks = json.load(taskFile)

print(f'Loaded tasks: \n{tasks}')

print("Starting to parse the json tasks ...")

createdRemindersCount = 0
createdListCount = 0

listInTasksCount = len(tasks["items"])
tasksCount = 0

print(f'Task lists count: {listInTasksCount}')


def getFormattedDateString(date, dateFormat, strFormat):
  dateObj = datetime.datetime.strptime(date, dateFormat)
  return f'date "{dateObj.strftime(strFormat)}"'


def getASDueDateProp(reminderDueDate):
  return f', due date: {reminderDueDate}' if reminderDueDate != None else ""


def getASBodyProp(reminderBody):
  return f', body: "{reminderBody}"' if reminderBody != None else ""


def getASCompletedProp(reminderCompleted):
  return f', completed: {reminderCompleted}' if reminderCompleted != None else ""


def getASCompletedDateProp(reminderCompletedDate):
  return f', completion date: {reminderCompletedDate}' if reminderCompletedDate != None else ""


def getCreateReminderListString(listName):
  return f'''
    tell application "Reminders"
    
    if not (exists list "{listName}") then
			make new list with properties {{name:"{listName}"}}
		end if
    
    end tell
  '''


def getCreateReminderWithPropString(
    listName, reminderName, reminderDueDate, reminderBody, reminderCompleted, reminderCompletedDate
):
  return f'''
    tell application "Reminders"
    
    set myList to list "{listName}"
    
    tell myList
      make new reminder with properties {{name: "{reminderName}"{getASDueDateProp(reminderDueDate)}{getASBodyProp(reminderBody)}{getASCompletedProp(reminderCompleted)}{getASCompletedDateProp(reminderCompletedDate)}}}
    end tell
  
  end tell
  '''


def createReminderListIfNotExist(listId, listName):

  print(f'Creating reminder list if not exist with listId: {listId}, with properties listName: {listName} ...')

  createReminderListStr = getCreateReminderListString(listName)

  print(f'For listId: {listId} - createReminderListStr: {createReminderListStr}')

  asResp = applescript.run(createReminderListStr)

  if asResp.code == 0:
    return True
  else:
    print(f'Error creating reminder list if not exist with listId: {listId}, with properties listName: {listName} ...')
    print(f'Error for listId: {listId} - Code: {asResp.code}, Error: {asResp.err}')
    return False


def createReminderWithProperties(
    reminderId, listName, reminderName, reminderDueDate, reminderBody, reminderCompleted, reminderCompletedDate
):

  print(f'Creating reminder with reminderId: {reminderId}, with properties listName: {listName}, reminderName: {reminderName}, reminderDueDate: {reminderDueDate}, reminderBody: {reminderBody}, reminderCompleted: {reminderCompleted} and reminderCompletedDate: {reminderCompletedDate} ...')

  createReminderWithPropStr = getCreateReminderWithPropString(
      listName, reminderName, reminderDueDate, reminderBody, reminderCompleted, reminderCompletedDate
  )

  print(f'For reminderId: {reminderId} - createReminderWithPropStr: {createReminderWithPropStr}')

  asResp = applescript.run(createReminderWithPropStr)

  if asResp.code == 0:
    return True
  else:
    print(f'Error for reminderId: {reminderId} - Code: {asResp.code}, Error: {asResp.err}')
    return False


def createRemindersForTasksInList(tasksInList):
  global tasksCount
  global createdRemindersCount
  global createdListCount
  listId = tasksInList['id'] if 'id' in tasksInList else "listIdDoesNotExist"
  listName = tasksInList['title'] if 'title' in tasksInList else "Other"
  remindersList = tasksInList['items'] if 'items' in tasksInList else []
  remindersInListCount = len(remindersList)
  createdRemindersForListCount = 0
  tasksCount = tasksCount + remindersInListCount

  print(f'Total reminders in list "{listName}": {remindersInListCount}')

  print(f'Reminders for list "{listName}": \n{remindersList}')

  if createReminderListIfNotExist(listId, listName):
    createdListCount = createdListCount + 1
    print(f'List = "{listName}" is created if not exists ...')
  else:
    errorInListsFile.write(f'{listId}\n')
    listName = DEFAULT_REMINDERS_LIST_NAME
    print(f'Using DEFAULT_REMINDERS_LIST_NAME: {DEFAULT_REMINDERS_LIST_NAME} instead of listName: {listName} due to error creating list ...')

  for reminder in remindersList:
    try:
      reminderId = reminder['id'] if 'id' in reminder else "reminderIdDoesNotExist"
      reminderName = reminder['title'] if 'title' in reminder else "reminderNameDoesNotExist"
      reminderDueDate = getFormattedDateString(reminder['due'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y 08:00 AM") if 'due' in reminder else None
      reminderBody = reminder['notes'] if 'notes' in reminder else None
      reminderCompleted = "true" if (('status' in reminder) & (reminder['status'] == "completed")) else None
      reminderCompletedDate = getFormattedDateString(reminder['completed'], "%Y-%m-%dT%H:%M:%S.%fZ", "%d/%m/%Y %H:%M:%S AM") if 'completed' in reminder else None

      if createReminderWithProperties(
        reminderId, listName, reminderName, reminderDueDate, reminderBody, reminderCompleted, reminderCompletedDate
      ):
        createdRemindersForListCount = createdRemindersForListCount + 1
        createdRemindersCount = createdRemindersCount + 1
        print(f'Created reminder with reminderId: {reminderId}, with properties listName: {listName}, reminderName: {reminderName}, reminderDueDate: {reminderDueDate}, reminderBody: {reminderBody}, reminderCompleted: {reminderCompleted} and reminderCompletedDate: {reminderCompletedDate} ...')
      else:
        errorInTasksFile.write(f'{reminderId}\n')
        print(f'Error creating reminder with reminderId: {reminderId}, with properties listName: {listName}, reminderName: {reminderName}, reminderDueDate: {reminderDueDate}, reminderBody: {reminderBody},  reminderCompleted: {reminderCompleted} and reminderCompletedDate: {reminderCompletedDate} ...')

    except Exception:
      print(f'Error creating reminder with properties reminderId: {reminderId}')
      print(f'Exception: {Exception}')
      print(f'Traceback: {traceback.format_exc()}')
      errorInTasksFile.write(f'{reminderId}\n')
      continue

  if remindersInListCount != createdRemindersForListCount:
    print(f'Diff: {remindersInListCount - createdRemindersForListCount}, Mismatch in reminder created and existing reminder count ...')
    print(f'remindersInListCount: {remindersInListCount}, createdRemindersForListCount: {createdRemindersForListCount}')


for tasksInList in tasks['items']:
  try:
    createRemindersForTasksInList(tasksInList)
  except Exception:
    print(f'Error creating reminders for tasks in list...')
    print(f'Exception: {Exception}')
    print(f'Traceback: {traceback.format_exc()}')
    continue

print(f'Total {createdListCount} lists created ... :)')

print(f'Total {createdRemindersCount} reminders created ... :)')

if listInTasksCount != createdListCount:
  print(f'Diff: {listInTasksCount - createdListCount}, Mismatch in list in tasks count and created list count ...')
  print(f'listInTasksCount: {listInTasksCount}, createdListCount: {createdListCount}')

if tasksCount != createdRemindersCount:
  print(f'Diff: {tasksCount - createdRemindersCount}, Mismatch in task counts and created reminder count ...')
  print(f'tasksCount: {tasksCount}, createdRemindersCount: {createdRemindersCount}')

taskFile.close()
errorInTasksFile.close()
errorInListsFile.close()
