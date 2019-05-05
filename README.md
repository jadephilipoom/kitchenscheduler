# Kitchen Scheduler 1000

Introducing the pika Kitchen Scheduler 1000...your flawless prototype goes full size!

## Get the program

Download the python program that runs the scheduler. You can do this in one of two ways:

### Option 1: Clone the github repository
   
Run `git clone https://github.com/jadephilipoom/kitchenscheduler.git` in a terminal.
This requires git to be installed, and will create a new directory called
`kitchenscheduler` for the code to live in.

### Option 2: Download manually

*Make a new directory.* This is important because the scheduler will create a
whole bunch of "autosave" files and you don't want them cluttering a directory
that doesn't have anything to do with the scheduler. On Linux or Mac, you can
do this with `mkdir kitchenschedule` in a terminal. On Windows, you can
download Linux. Or you can go to an Athena cluster and use their Linux.

Once you create your directory, download the file by going to
[https://raw.githubusercontent.com/jadephilipoom/kitchenscheduler/master/interactive_schedule.py](https://raw.githubusercontent.com/jadephilipoom/kitchenscheduler/master/interactive_schedule.py)
and saving the page. Move the file to your new directory.

## Get the responses

Go to the Google Sheets page where the form responses are saved. Export the
file as a CSV and move it to the same directory as the program.

## First steps

Open a terminal and navigate to the directory where the scheduler and responses live. Run:

`python3 interactive_schedule.py responses.csv`

(replacing "responses.csv" with whatever you called your CSV file)

### Errors and warnings

You might get errors when you run this. If you do, the errors will give you
instructions about what to do. If the wording of the questions on the Google
form has changed, you'll need to change those headers in the code (search for
"FIELD_HEADERS"; you only have to change it in one place).

You'll also probably see a warning that says something like:

`pairing requests contained some names that were not recognized
and therefore ignored: ciara, helen.`

`if these are names for people who did in fact sign up, please
change them in the data file to match the person's kerberos or
email address.`

This means what it says: some people were requested as cooking or
cleaning-mates who aren't on the list of kerberoses that signed up for
mealplan. If the person genuinely didn't sign up, that's fine, but be careful
of cases where the requestor wrote someone's name instead of their kerberos. If
this happens, go to the responses CSV and change the name to a kerberos/email
address.

Finally, you'll get some warnings saying something like:

```
jpika is unavailable for > 2/3 of available shift times (11 out of 14)
```

This is just to let you know that someone put themselves as absolutely
unavailable for a lot of timeslots, so you can yell at them if they're being
dumb.

### Get started!

Following any warnings, you'll see statistics about who asked for which shifts
and some tips about how to use the scheduler. **Read the tips.** They will tell
you what to do initially (like display the current status and display the
possible commands). Definitely read the list of commands so you have an idea
what the scheduler can do -- it might make your life easier.

Type "exit" to leave the scheduler. When you do, it will autosave (and give you
instructions about how to restore the state).
