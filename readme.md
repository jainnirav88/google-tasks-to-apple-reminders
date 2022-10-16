# google-tasks-to-apple-reminders

GoogleTasksToAppleReminders is python program to move google tasks to apple reminders with the help of applescript.

## Instructions

1. Clone the repository by running `git clone https://github.com/jainnirav88/google-tasks-to-apple-reminders`.
2. Export google tasks from google takeout, detailed instruction can be found at [Export your data from Google Tasks](https://support.google.com/tasks/answer/10017961) and at [How to download your Google data](https://support.google.com/accounts/answer/3024190). Google tasks should be json format after unzip (if exported in zip format).
3. Move exported tasks json file into same folder as GoogleTasksToAppleReminders.py folder (current folder) OR add file location in TASKS_FILE_LOCATION of **.env** file
4. Install all the required libraries by running `pip3 install -r requirements.txt`
5. Finally run the bot by executing `python3 GoogleTasksToAppleReminders.py`