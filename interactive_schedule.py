import sys, csv

# Constant strings used to refer to questions and answers on the survey
NAME = "Name"
NEW = "New"
FULL_OR_HALF = "FullOrHalf"
COOK = "Cook"
BIGCOOK = "BigCook"
MEDCOOK = "MedCook"
CLEAN = "Clean"
PAIR = "Pair"
COOK_MON = "CookMon"
CLEAN_MON = "CleanMon"
COOK_TUE = "CookTue"
CLEAN_TUE = "CleanTue"
COOK_WED = "CookWed"
CLEAN_WED = "CleanWed"
COOK_THU = "CookThu"
CLEAN_THU = "CleanThu"
COOK_FRI = "CookFri"
CLEAN_FRI = "CleanFri"
COOK_SAT = "CookSat"
CLEAN_SAT = "CleanSat"
COOK_SUN = "CookSun"
CLEAN_SUN = "CleanSun"

# Change these if the wording of survey answers changes
FULL = "Full"
HALF = "Half"
YES = "Yes"
MAYBE = "Maybe"
NO = "No"

# Text in the input CSV that corresponds to each survey question
# Note: this needs to change if the wording of survey questions changes
FIELD_HEADERS = { 
        NAME : "Name",
        NEW : "New",
        FULL_OR_HALF : "FullOrHalf",
        COOK : "Cook",
        BIGCOOK : "BigCook",
        CLEAN : "Clean",
        PAIR : "Pair",
        COOK_MON : "CookMonday",
        CLEAN_MON : "CleanMonday",
        COOK_TUE : "CookTuesday",
        CLEAN_TUE : "CleanTuesday",
        COOK_WED : "CookWednesday",
        CLEAN_WED : "CleanWednesday",
        COOK_THU : "CookThursday",
        CLEAN_THU : "CleanThursday",
        COOK_FRI : "CookFriday",
        CLEAN_FRI : "CleanFriday",
        COOK_SAT : "CookSaturday",
        CLEAN_SAT : "CleanSaturday",
        COOK_SUN : "CookSunday",
        CLEAN_SUN : "CleanSunday"
        }
YES_NO_QUESTIONS = [NEW]
YES_MAYBE_NO_QUESTIONS = [COOK, BIGCOOK, CLEAN, COOK_MON, CLEAN_MON, COOK_TUE, CLEAN_TUE, COOK_WED, CLEAN_WED, COOK_THU, CLEAN_THU, COOK_FRI, CLEAN_FRI, COOK_SAT, CLEAN_SAT, COOK_SUN, CLEAN_SUN]

SHIFT_TYPES = ["bigcook", "littlecook", "clean"] # N.B. if names are changed here, also change them in Shift.__init__

MON = "Mon"
TUE = "Tue"
WED = "Wed"
THU = "Thu"
FRI = "Fri"
SAT = "Sat"
SUN = "Sun"
DAYS = [MON, TUE] #, WED, THU, FRI, SAT, SUN]

# codes for weeks
WEEK1 = 1
WEEK2 = 2

# codes for types of "maybe" answers
MAYBE_TYPE = 2
MAYBE_TIME = 3
MAYBE_BIGCOOK = 4

# return codes for input handling
REDISPLAY = True
ASK_AGAIN = False

# The exception type raised when the input can't be handled properly.
class InputError(Exception):
    pass

class Shift:
    def paired(s1, s2):
        return (s1 != s2 and s1.day == s2.day and s1.week == s2.week and s1.is_cooking == s2.is_cooking)
    
    def __init__(self, shift_type, day, week):
        self.type = shift_type
        self.day = day
        self.week = week
        
        self.is_cooking = False 
        self.is_big_cooking = False 
        if self.type == "bigcook":
            self.is_big_cooking = True
            self.is_cooking = True
        elif self.type == "littlecook":
            self.is_cooking = True
        elif self.type != "clean":
            print("Error: unrecognized shift type %s" %self.type)
            sys.exit()

        self.time = ("Cook" if self.is_cooking else "Clean") + day
    
    def category(self):
        if self.is_big_cooking:
            return "big" + self.time.lower()
        return self.time.lower()

    def __str__(self):
        return self.category() + str(self.week)

def generate_shifts():
    shifts = []
    for week in [WEEK1, WEEK2]:
        for day in DAYS:
            for t in SHIFT_TYPES:
                s = Shift(t, day, week)
                shifts.append(s)
                if not s.is_cooking:
                    # duplicate cleaning shifts
                    shifts.append(Shift(t, day, week))
    return shifts

def get_input(prompt="Enter your move or type 'help' for options: "):
    return input(prompt).strip().lower()

def get_args(input_text, lead_words, nargs):
    args = [a.strip() for a in input_text.split(" ") if a.strip() != ""][ len(lead_words.split(" ")):]
    if len(args) != nargs:
        raise InputError("Unexpected number of arguments to '%s'! Expected %s arguments but got %s : %s" %(lead_words, nargs, len(args), ", ".join(args)))
    return args

def make_note(name, shift, maybe_code):
    note = None
    if maybe_code == MAYBE_TYPE:
        note = "%s only 'maybe' wants to do a %s shift" %(name, "cooking" if shift.is_cooking else "cleaning")
    elif maybe_code == MAYBE_TIME:
        note = "%s only 'maybe' is available for %s on %s" %(name, "cooking" if shift.is_cooking else "cleaning", shift.day)
    elif maybe_code == MAYBE_BIGCOOK:
        note = "%s only 'maybe' wants to big cook" %name
    else:
        print("Unexpected Error: Unrecognized maybe-code %s" %maybe_code)
    return note

def shift_name(shift):
    return str(shift)


class Scheduler:
    def __init__(self, data):
        self.data = data
        self.shifts = generate_shifts()
        self.people = list(data.keys())
        self.shift_person_rules = {}  # dictionary mapping rule name (string) to a function with type person -> shift -> bool (true if OK, false if this pairing is excluded)
        self.person_person_rules = {} # dictionary mapping rule name (string) to a function with type person -> person -> bool (true if OK, false if this pairing is excluded)
        self.rule_commands = {}
        self.rule_counter = 0
        self.other_assignments = {week : [] for week in [WEEK1, WEEK2]}
        self.assignments = {} # dictionary mapping shift to person and signify that a person is assigned to that shift 
        self.autoassign = True

    def run(self):
        self.step_and_display()
        self.display_welcome()
        while True:
            cmd = get_input()
            if cmd == "exit":
                return
            redisplay = self.handle_input(cmd)
            if redisplay:
                self.step_and_display()
                if self.is_complete():
                    self.display_complete()
                    cmd = get_input(msg="Type 'exit' to end the program; type anything else to continue: ")
                    if cmd == "exit":
                        return
    
    def is_complete(self):
        return all([s in self.assignments for s in self.shifts])

    def get_answer(self, name, shift):
        relevant_responses = [data[name][shift.time]]
        if shift.is_cooking:
            relevant_responses.append(data[name][COOK])
            if shift.is_big_cooking:
                relevant_responses.append(data[name][BIGCOOK])
        else: 
            relevant_responses.append(data[name][CLEAN])
        if NO in relevant_responses:
            return NO
        if MAYBE in relevant_responses:
            return MAYBE
        return YES

    def get_notes(self, p, s):
        notes = []
        if self.data[p][s.time] == MAYBE:
            notes.append(MAYBE_TIME)
        if s.is_cooking and (self.data[p][COOK] == MAYBE):
            notes.append(MAYBE_TYPE)
            if s.is_big_cooking and (self.data[p][BIGCOOK] == MAYBE):
                notes.append(MAYBE_BIGCOOK)
        elif self.data[p][CLEAN] == MAYBE:
            notes.append(MAYBE_TYPE)
        return notes

    def get_remaining_shifts(self):
        remaining_shifts = {p : (1 if data[p][FULL_OR_HALF] == HALF else 2) for p in self.people}
        for p in self.assignments.values():
            remaining_shifts[p] -= 1
        for week in self.other_assignments:
            for p in self.other_assignments[week]:
                remaining_shifts[p] -= 1
        return remaining_shifts

    def get_warnings(self):
        # TODO: warn when a rule is violated 
        possibilities_by_shift = self.get_possibilities_by_shift()
        remaining_shifts = self.get_remaining_shifts()
        has_shift_for_week = { week : {p : False for p in self.people} for week in [WEEK1, WEEK2] }
        warnings = []
        for s, p in self.assignments.items():
            # warn if someone is doing multiple shifts in the same week
            if has_shift_for_week[s.week][p]:
                warnings.append("%s has multiple shifts in the same week (week %s)" %(p, s.week))
            has_shift_for_week[s.week][p] = True
            # warn if someone is doing too many shifts
            if remaining_shifts[p] < 0:
                warnings.append("%s is doing too many shifts" %p)
            # warn if someone is assigned to a thing they said no to
            if self.data[p][s.time] == NO:
                warnings.append("%s is assigned to shift %s even though they said they are unavailable" %(p, s))
            if self.data[p][COOK] == NO and s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cooking" %(p, s))
            if self.data[p][CLEAN] == NO and not s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cleaning" %(p, s))
            if self.data[p][BIGCOOK] == NO and s.is_big_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to big cooking" %(p, s))
        # warn if no one is available for a shift
        for s, possibilities in possibilities_by_shift.items():
            if len(possibilities) == 0:
                warnings.append("No one is available for shift %s" %s)
        return warnings

    # mapping from each person to all unassigned shifts that they could work
    def get_shifts_by_people(self, possibilities_by_shift):
        shifts_by_people = {p : [] for p in self.people}
        for s in possibilities_by_shift:
            if s in self.assignments:
                continue
            for p, _ in possibilities_by_shift[s]:
                shifts_by_people[p].append(s)
        return shifts_by_people

    def get_suggestions(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        shifts_by_people = self.get_shifts_by_people(possibilities_by_shift)
        remaining_shifts = self.get_remaining_shifts()
        available_people = list(filter(lambda p : remaining_shifts[p] > 0, self.people))
        suggestions = [] 
        # suggest pairing people who want to work together
        for p1 in available_people:
            for s1 in shifts_by_people[p1]:
                for s2 in self.assignments:
                    if self.assignments[s2] in self.data[p1][PAIR] and Shift.paired(s1, s2):
                        justification = "so %s and %s can work together as requested by %s" %(p1, self.assignments[s2], p1)
                        if p1 in self.data[assignments[s2]][PAIR]:
                            justification += " and %s both" %assignments[s2]
                        suggestions.append(("assign %s %s" %(p1, s1), justification))
        # suggest new people for non-cleaning shifts if they preferred that
        for p in filter(lambda p : data[p][NEW], available_people):
            if data[p][COOK] == YES or (data[p][COOK] == MAYBE and data[p][CLEAN] == MAYBE):
                # they consider cooking better or equal, and could have both types available
                available_cooking_shifts = list(filter(lambda s : shift.is_cooking, shifts_by_people[p]))
                available_cleaning_shifts = list(filter(lambda s : not shift.is_cooking, shifts_by_people[p]))
                if len(available_cleaning_shifts) == 0:
                    continue # if they can't do any cleaning shifts anyway, then there's no suggestion to make
                for s in available_cooking_shifts:
                    suggestions.append(("assign %s %s" %(p, s), "because new people tend to be far happier (and less likely to drop) on cooking shifts than cleaning ones"))
        # if there's only one person left without a 'maybe' answer on a particular shift, suggest them
        for s in possibilities_by_shift:
            if s in self.assignments:
                continue
            yes_people = list(filter(lambda x : len(x[1]) == 0, possibilities_by_shift[s]))
            if len(yes_people) == 1:
                suggestions.append(("assign %s %s" %(yes_people[0][0], s), "because they are the only remaining person who said 'yes' to all the shift's availability/shift-type questions")) 
        suggestions_reformatted = {}
        for cmd, justification in suggestions:
            if cmd in suggestions_reformatted:
                suggestions_reformatted[cmd].append(justification)
            else:
                suggestions_reformatted[cmd] = [justification]
        return suggestions_reformatted

    def get_possibilities_by_shift(self):
        possibilities_by_shift = { s : [] for s in self.shifts}
        has_shift_for_week = { week : {p : False for p in self.people} for week in [WEEK1, WEEK2] }
        remaining_shifts = self.get_remaining_shifts() # remaining num. of shifts per person
        unassigned_shifts = [s for s in self.shifts if s not in self.assignments]
        # first do assignments
        for s, name in self.assignments.items():
            possibilities_by_shift[s] = [(name, [])]
            has_shift_for_week[s.week][name] = True
        for week in self.other_assignments:
            for name in self.other_assignments[week]:
                has_shift_for_week[week][name] = True
        # next, aggregate other possibilities
        for s in unassigned_shifts:
            for p in self.people:
                if remaining_shifts[p] <= 0 or has_shift_for_week[s.week][p]:
                    continue
                if self.get_answer(p, s) != NO:
                    possibilities_by_shift[s].append((p, self.get_notes(p, s)))
        # apply rules
        for r, rule_okay in self.shift_person_rules.items():
            for s in self.shifts:
                possibilities_by_shift[s] = [(p, notes) for p, notes in possibilities_by_shift[s] if rule_okay(p, s) or s in self.assignments]
        for rule_okay in self.person_person_rules.values():
            for s1 in self.assignments:
                p1 = possibilities_by_shift[s1][0][0]
                for s2 in unassigned_shifts:
                    if Shift.paired(s1, s2):
                        possibilities_by_shift[s2] = [(p2, notes) for p2, notes in possibilities_by_shift[s2] if rule_okay(p1, p2)]
        return possibilities_by_shift

    # auto-assigns people if they are the last one who can do a shift
    # N.B. does not auto-assign people if they only have one more shift they can do, because if you have more people than shifts that's not an obvious choice
    def auto_assign(self, possibilities_by_shift):
        if not self.autoassign:
            return None
        shifts_by_people = self.get_shifts_by_people(possibilities_by_shift)
        remaining_shifts = self.get_remaining_shifts() # remaining num. of shifts per person
        # assign people who are the last option for a shift
        for s in self.shifts:
            if s in self.assignments:
                continue
            options = possibilities_by_shift[s]
            if len(options) == 1:
                name = options[0][0] 
                print("Auto-assigning %s to shift %s because they are the only remaining possibility" %(name, s))
                return (s, name)
            if len(options) == 2 and not s.is_cooking: # don't autoassign cooking shifts because designating the big cook is kind of an important choice
                for s2 in self.shifts:
                    if Shift.paired(s, s2) and len(possibilities_by_shift[s2]) == 2:
                        if all(map(lambda p : p in possibilities_by_shift[s2], options)) and all(map(lambda p : p in options, possibilities_by_shift[s2])):
                            # the 2 possibilities for each shift are the same 2 people; auto-assign them
                            # it is sufficient to auto-assign one, the next round will catch the next one
                            print("Auto-assigning %s to shift %s because they and %s are the only remaining possibilities for two simultaneous shifts" %(options[0][0], s, options[1][0]))
                            return (s, options[0][0])

    def step_and_display(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        new_assignment = self.auto_assign(possibilities_by_shift)
        # repeat adding new assignments and recalculating until no one else can be automatically assigned
        while new_assignment != None:
            s, name = new_assignment
            self.assignments[s] = name
            possibilities_by_shift = self.get_possibilities_by_shift()
            new_assignment = self.auto_assign(possibilities_by_shift)
        self.display_state()
 
    def handle_input(self, x):
        try:
            return self.handle_input_cases(x)
        except InputError as err:
            print(err)
            return ASK_AGAIN

    def handle_input_cases(self, x):
        if x == "help":
            self.display_help()
            return ASK_AGAIN
        elif x == "show status":
            return REDISPLAY
        elif x == "show rules":
            self.display_rules()
            return ASK_AGAIN
        elif x == "show assignments":
            self.display_assignments()
            return ASK_AGAIN
        elif x == "show notes":
            self.display_notes()
            return ASK_AGAIN
        elif x == "show suggestions":
            self.display_suggestions()
            return ASK_AGAIN
        elif x == "autoassign off":
            self.set_autoassign(False)
            return ASK_AGAIN
        elif x == "autoassign on":
            action = ASK_AGAIN if self.autoassign else REDISPLAY # only redisplay if autoassign was previously off
            self.set_autoassign(True)
            return action 
        elif x.startswith("assign"):
            self.handle_assignment(x)
            return REDISPLAY
        elif x.startswith("unassign"):
            self.handle_unassignment(x)
            return REDISPLAY
        elif x.startswith("remove rule"):
            self.handle_remove_rule(x)
            return REDISPLAY
        elif x.startswith("show notes"):
            self.handle_show_notes(x)
            return ASK_AGAIN
        elif x.startswith("exclude"):
            self.handle_exclude(x)
            return REDISPLAY
        else:
            print("Error: Input not recognized.")
            self.display_commands()
            return ASK_AGAIN

    # check that an input argument does in fact correspond to a person
    def check_person_arg(self, x, new_ok=False):
        if new_ok and x == "new":
            return
        if x not in self.people:
            raise InputError("Unrecognized person %s. Recognized people are : " %(x, ", ".join(self.people)))
 
    # check that an input argument does in fact correspond to a shift
    def check_shift_arg(self, x):
        if x == "other":
            return
        shift_names = [shift_name(s) for s in self.shifts]
        if x not in shift_names:
            raise InputError("Unrecognized shift %s. Recognized shifts are : %s" %(x, ", ".join(list(set(shift_names)))))
    
    def set_autoassign(self, value):
        new_status = "on" if value else "off" 
        opposite_status = "off" if value else "on" 
        if self.autoassign == value:
            print("Well, autoassign is already %s, so...sure?" %new_status)
        else:
            print("Turning autoassignment %s. Write 'autoassign %s' to turn it back %s." %(new_status, opposite_status, opposite_status))
            self.autoassign = value

    # Expects: assign <person> {<shift>, other}
    def handle_assignment(self, cmd):
        person, shift = get_args(cmd, "assign", 2)
        self.check_person_arg(person)
        # check for case in which we assign someone to e.g. 'bigcookmon' and they get assigned to both weeks at once; treat as though it's two commands
        if not (shift.endswith("1") or shift.endswith("2")):
            self.handle_assignment(" ".join(["assign", person, shift + "1"]))
            self.handle_assignment(" ".join(["assign", person, shift + "2"]))
            return
        self.check_shift_arg(shift)
        msg = "Assigning %s to shift %s" %(person, shift)
        if shift == "other1":
            self.other_assignments[WEEK1].append(person)
            print(msg)
            return
        elif shift == "other2":
            self.other_assignments[WEEK2].append(person)
            print(msg)
            return
        else:
            for s in self.shifts:
                if shift_name(s) == shift and s not in self.assignments:
                    self.assignments[s] = person
                    print(msg)
                    return
        # if we get here, then no shifts were unclaimed
        raise InputError("Could not assign shift; all shifts of type %s are taken. Did you type the correct week?" %shift)

    # Expects: unassign <person> {<shift>, other}
    def handle_unassignment(self, cmd):
        person, shift = get_args(cmd, "unassign", 2)
        self.check_person_arg(person)
        # check for case in which we unassign someone from e.g. 'bigcookmon' and they get unassigned from both weeks at once; treat as though it's two commands
        if not (shift.endswith("1") or shift.endswith("2")):
            self.handle_unassignment(" ".join(["unassign", person, shift + "1"]))
            self.handle_unassignment(" ".join(["unassign", person, shift + "2"]))
            return
        self.check_shift_arg(shift)
        msg = "Unassigning %s from shift %s" %(person, shift)
        if shift == "other1":
            if person in self.other_assignments[WEEK1]:
                self.other_assignments[WEEK1].remove(person) 
                print(msg)
                return
        if shift == "other2":
            if person in self.other_assignments[WEEK2]:
                self.other_assignments[WEEK2].remove(person) 
                print(msg)
                return
        else:
            for s in self.assignments:
                if shift_name(s) == shift and self.assignments[s] == person:
                    del self.assignments[s]
                    print(msg)
                    return
        # if we get here, then the person was not assigned to that shift
        raise InputError("%s is not currently assigned to shift %s. Did you type the right week?" %(person, shift))

    # Expects: remove rule <rule name>
    def handle_remove_rule(self, cmd):
        r = get_args(cmd, "remove rule", 1)[0]
        if r not in self.rule_commands:
            raise InputError("Unrecognized rule name %s. Recognized rule names are: %s" %(r, ", ".join(self.rule_commands.keys())))
        if r in self.shift_person_rules:
            del self.shift_person_rules[r]
        else:
            del self.person_person_rules[r]
        print("Removing rule %s (%s)" %(r, self.rule_commands[r]))
        del self.rule_commands[r]

    def handle_exclude_person_person(self, rule_name, p1, p2):
        if p1 == p2 and p1 != "new":
            raise InputError("You cannot exclude someone from cooking with themselves. What's your problem?")
        cond1 = lambda p : p == p1
        cond2 = lambda p : p == p2
        if p1 == "new":
            cond1 = lambda p : self.data[p][NEW]
        if p2 == "new":
            cond2 = lambda p : self.data[p][NEW]
        self.person_person_rules[rule_name] = lambda px, py : not ((cond1(px) and cond2(py)) or (cond2(px) and cond1(py)))

    def handle_exclude_person_shift(self, rule_name, p1, x):
        cond1 = lambda p : p == p1
        cond2 = lambda s : shift_name(s) == x
        if p1 == "new":
            cond1 = lambda p : self.data[p][NEW]
        if x in SHIFT_TYPES:
            cond2 = lambda s : s.type == x
        self.shift_person_rules[rule_name] = lambda p, s : not (cond1(p) and cond2(s))
 
    # Expects: exclude {<person>, new} {<shift>, <person>, new}
    def handle_exclude(self, cmd):
        p1, x = get_args(cmd, "exclude", 2)
        rule_name = "rule" + str(self.rule_counter)
        self.check_person_arg(p1, new_ok=True)
        shift_names = [shift_name(s) for s in self.shifts]
        if x in shift_names or x in SHIFT_TYPES:
            self.handle_exclude_person_shift(rule_name, p1, x)
        elif x == "other":
            raise InputError("'other' shifts cannot be used in 'exclude', and there's no reason to do it anyway, so stoppit")
        else:
            self.check_person_arg(x, new_ok=True)
            self.handle_exclude_person_person(rule_name, p1, x)
        self.rule_counter += 1
        self.rule_commands[rule_name] = cmd
        print("Adding rule %s (%s)" %(rule_name, cmd))

    # N.B. this function is not responsible for the plain 'show notes' version of the command
    # Expects: show notes <person>
    def handle_show_notes(self, cmd):
        p = get_args(cmd, "show notes", 1)
        self.check_person_arg(p)
        display_notes(p)

    def display_notes(self,person=None):
        notes = []
        for s, options in self.get_possibilities_by_shift().items():
            for p, maybe_notes in options:
                if person == None or person == p:
                    for n in maybe_notes:
                        notes.append(make_note(p, s, n))
        print("Notes:")
        notes = list(set(notes))
        notes.sort()
        for n in notes:
            print("\t- " + n)

    def display_tips(self):
        print(" - If a name has parentheses, that means the person answered 'maybe' to questions about that shift time/type")
        print(" - To see details about 'maybe' answers, type 'show notes' or 'show notes <person's name>'")
        print(" - The 'other' category is for miscellaneous shifts, like tiny cook, fridge ninja, or brunch cook")
        print(" - Type 'show suggestions' to get suggestions for next moves")

    def display_commands(self):
        print("Possible commands (everything is case-insensitive):")
        print("\texit\t\t- close program")
        print("\tshow status\t\t- display the current state of assignments/possibilities")
        print("\tshow rules\t\t- display the rules currently in effect")
        print("\tshow notes\t\t- display the reasons for any 'maybe' parentheses currently displayed")
        print("\tshow notes <person>\t- display the reasons for any 'maybe' parentheses currently displayed around <person>")
        print("\tshow assignments\t- display the shift assignments currently in effect")
        print("\tshow suggestions\t- suggest next moves")
        print("\tassign <person> <shift>\t- assign <person> to <shift> (e.g. 'assign %s %s')" %(self.people[0], shift_name(self.shifts[0])))
        print("\tassign <person> other\t- assign <person> to some shift that doesn't appear here (e.g. fridge ninja or tiny cook), so that they don't show up as possibilities for other shifts")
        print("\tunassign <person> <shift>\t- unassign <person> from <shift>")
        print("\tautoassign off\t\t- turn off autoassign (on by default), which is when the system automatically identifies and fills shifts that can only be filled one way")
        print("\tautoassign on\t\t- turn autoassign back on")
        print("\texclude <person> <shift_type>\t- exclude <person> from certain shift types ('%s',' %s', or '%s')" %tuple(SHIFT_TYPES))
        print("\texclude new <shift_type>\t- exclude all people new to mealplan from certain shift types ('%s', '%s', or '%s')" %tuple(SHIFT_TYPES))
        print("\texclude <person> <shift>\t- exclude <person> from a certain shift (e.g. '%s' or '%s')" %(shift_name(self.shifts[0]), shift_name(self.shifts[3])))
        print("\texclude new <shift>\t\t- exclude all people new to mealplan from a certain shift (e.g. '%s' or '%s')" %(shift_name(self.shifts[0]), shift_name(self.shifts[3])))
        print("\texclude <person> <person>\t- exclude two people from working together") 
        print("\texclude new <person>\t- exclude someone from working with new people") 
        print("\texclude new new\t\t- exclude possibilities where two people who are *both* new to mealplan would work together") 
        print("\tremove rule <rule name>\t- remove a rule based on the name shown by 'show rules'")
    
    def display_help(self):
        print("Tips:")
        self.display_tips()
        print("")
        self.display_commands()

    def display_complete(self):
        print("ALL SHIFTS ASSIGNED!")
        remaining_shifts = self.get_remaining_shifts()
        nonzero_remaining_shifts = {p : rem for p, rem in remaining_shifts.items() if rem != 0}
        if len(nonzero_remaining_shifts) != 0:
            print("Some people have remaining shifts (they can be assigned as tiny cooks etc):")
            for p, rem in remaining_shifts.items():
                if rem != 0:
                    print("%s : %s shifts remaining" %(p, rem))

    def display_welcome(self):
        print("**** Welcome to the Kitchen Scheduler 1000! ****")
        self.display_tips()
        print(" - To show all possible commands, type 'help'") # this tip is separate so it doesn't show up in the help message, that would be dumb
        print("")

    def display_suggestions(self):
        suggestions = self.get_suggestions()
        print("Suggested moves:")
        for cmd, justifications in suggestions.items():
            print("\t-%s (%s)" %(cmd, " and ".join(justifications)))
        if len(suggestions) == 0:
            print("\t No suggestions, sorry!")

    def display_rules(self):
        for r in (sorted(self.rule_commands.keys())):
            print("%s : %s" %(r, self.rule_commands[r]))
        if len(self.rule_commands) == 0:
            print("No rules yet!")

    def display_assignments(self):
        for s in self.assignments:
            print("%s : %s" %(s, self.assignments[s]))
        if len(self.assignments) == 0:
            print("No assignments yet!")

    def display_state(self):
        table = {shift_name(s) : [] for s in self.shifts}
        possibilities_by_shift = self.get_possibilities_by_shift()
        week, day = None, None
        for s in possibilities_by_shift:
            if s in self.assignments:
                table[shift_name(s)].append("[" + possibilities_by_shift[s][0][0] + "]")
            else:
                for p, maybe_notes in possibilities_by_shift[s]:
                    display_p = p
                    for n in maybe_notes:
                        display_p = "(" + display_p + ")"
                    table[shift_name(s)].append(display_p)

        for s in table:
            table[shift_name(s)] = list(set(table[shift_name(s)])) # remove duplicate entries for cleaning shifts

        already_printed = []
        for s in self.shifts:
            if s.week != week:
                print("")
                print("Week %s" %s.week)
                print("======")
                print("other%s: %s" %(s.week, ", ".join(self.other_assignments[s.week])))
                print("")
            elif s.day != day:
                print("")
            day = s.day
            week = s.week
            if shift_name(s) not in already_printed: # avoids duplicating the cleaning shifts
                already_printed.append(shift_name(s))
                print("%s (%s) : %s" %(s, len(table[shift_name(s)]), "; ".join(sorted(table[shift_name(s)])))) 
        print("")
        for warning in self.get_warnings():
            print("WARNING: %s" %warning)

def clean_data(data):
    names = [r[NAME].lower() for r in data]
    datab = []
    datac = {}

    # check that all fields exist and have acceptable answers
    for row in data:
        for question in FIELD_HEADERS.values():
            if not question in row:
                malformatted_msg = "Malformatted input; could not find the field %s. If the question name changed, you need to update the code with the new name (search the code for 'FIELD_HEADERS')." %question
                print(malformatted_msg)
        r = { field : row[FIELD_HEADERS[field]] for field in FIELD_HEADERS } 
        for field in YES_NO_QUESTIONS: # strict yes/no answers
            if r[field] != YES and r[field] != NO:
                print("Unexpected answer to yes/no question: got %s, expected %s or %s" %(r[field], YES, NO))
        for field in YES_MAYBE_NO_QUESTIONS: # yes/maybe/no answers
            if r[field] != YES and r[field] != NO and r[field] != MAYBE:
                print("Unexpected answer to yes/maybe/no question: got %s, expected %s, %s, or %s" %(r[field], YES, MAYBE, NO))
        if r[FULL_OR_HALF] != FULL and r[FULL_OR_HALF] != HALF:
            print("Unexpected answer to '%s' question: got %s, expected %s or %s" %(FULL_OR_HALF, r[FULL_OR_HALF], FULL, HALF))
        datab.append(r)

    # make all people's names lowercase and make sure requested pairs actually signed up for mealplan
    for r in datab:
        pair = []
        for name in r[PAIR]:
            if name in names:
                pair.append(name)
            else:
                print("WARNING: removing preference for %s to be paired with %s, since %s did not sign up. If this is just a different name for someone who did in fact sign up, please change it in the data file." %(r[NAME],name,name))
        r[PAIR] = pair
        r[NEW] = True if r[NEW] == YES else False
        datac[r[NAME].lower()] = r 
    names = list(datac.keys())
    for i in range(len(names)):
        for j in range(i+1, len(datac)):
            if names[i] == names[j]:
                print("ERROR: two occurrences of name %s (case-insensitive)", names[i])
                sys.exit()
    return datac

def parse_data(dataf):
    datar = csv.DictReader(dataf)
    data = []
    for row in datar:
        if row[PAIR] == None:
            row[PAIR] = []
        else:
            row[PAIR] = [name.lower() for name in row[PAIR].split(";") if name != ""]
        data.append(row)
    datac = clean_data(data)
    return datac


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python schedule.py [data file]")
        sys.exit()

    dataf = open(sys.argv[1])
    data = parse_data(dataf)
    Scheduler(data).run()
    # TODO: save/load functionality
    # TODO: add heuristic/brute force search at some point?
    # when you unassign someone for a shift, but they were the last person available and said all-yes, they still show up as if they are assigned because the format is ambiguous here. Is this an issue? 

# Questions
# What would be a good output format? Assignments or schedule or csv?
# save/load functionality?

# TODO: right now, making a rule unassigns people. We don't want that.
