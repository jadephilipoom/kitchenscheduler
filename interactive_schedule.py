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
    id_counter = 0
    def __init__(self, shift_type, day, week):
        self.type = shift_type
        self.day = day
        self.week = week
        # TODO: try removing the id thing
        self.id = Shift.id_counter
        Shift.id_counter += 1
        
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

    def __str__(self):
        if self.is_big_cooking:
            return ("big" + self.time.lower() + str(self.week))
        return self.time.lower() + str(self.week)

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

def get_input(self, prompt="Enter your move or type 'help' for options: "):
    x = input(prompt).strip().lower()

def get_args(input_text, lead_words, nargs):
    args = [a.strip() for a in input_text.split(" ") if a.strip() != ""]
    nlead = len(lead_words.split(" "))
    if len(args) - nlead == nargs:
        return args
    raise InputError("Unexpected number of arguments to '%s'! Expected %s arguments but got %s : %s" %(lead_words, nargs, len(args) - nlead, ", ".join(args[nlead:])))

class Command:
    # TODO: maybe move these out of this class
    PERSON_ARG = "<person>"
    SHIFT_ARG = "<shift>"
    PEOPLE = None
    SHIFTS = None

    # arg_types should be a list of strings, where each string can be either PERSON_ARG, SHIFT_ARG, or a constant 
    def __init__(self, name, arg_types, handler, descr):
        self.name = name
        self.arg_types = arg_types
        self.handler = handler
        self.descr = descr
        self.name_args = self.name.split(" ")
    
    def check_arg(arg, arg_type):
        if arg_type == PERSON_ARG:
            if not arg in PEOPLE:
                raise InputError("Unrecognized person %s. Recognized people are : " %(arg, ", ".join(Command.PEOPLE)))
        elif arg_type == SHIFT_ARG:
            if not arg in SHIFTS:
                raise InputError("Unrecognized shift %s. Recognized shifts are : %s" %(arg, ", ".join(Command.SHIFTS)))
        elif arg != arg_type:
            raise InputError("Unexpected argument to %s: '%s'. Expected something like '%s'" %(self, arg, arg_type))

    # returns None if the command is not one of this type, and raises an error if the incorrect number/type of arguments are provided
    def get_args(self, cmd):
        if not cmd.startswith(self.name):
            return None
        args = [a.strip() for a in input_text.split(" ") if a.strip() != ""][len(self.name_args):]
        if len(args) == len(arg_types):
            for a, t in zip(args, arg_types):
                self.check_arg(arg, arg_type) # raises an exception if the argument isn't the right type
            return args
        raise InputError("Unexpected number of arguments to '%s'. Expected %s arguments but got %s : %s" %(self, len(arg_types), len(args), ", ".join(args)))

    def __str__(self):
        return self.name

# we want the commands listed only ONCE
# maybe in scheduler init, we create all the commands, initializing people and shifts and handlers, and add them to a constant list
# then in input loop, we go through the list and call the right handlers
# in display_help, we also go through the same list

# Problem: in help we want all combinatorial options listed out, with separate messages
# in handlers and input loop, we don't want them separate

# idea: just give all the things the same handler, dumbass

class Scheduler:
    def __init__(self, data):
        self.data = data
        self.shifts = generate_shifts()
        self.people = list(data.keys())
        self.shift_person_rules = {}
        self.person_person_rules = {}
        self.rule_commands = {}
        self.rule_counter = 0
        self.other_assignments = {week : [] for week in [WEEK1, WEEK2]}
        self.assignments = {}
        self.autoassign = True
        self.initialize_commands()

    def initialize_commands(self)
        # initialize the Command class with people and shifts, so it can check its arguments
        Command.PEOPLE = self.people
        Command.SHIFTS = list(set([shift_name(s) for s in self.shifts]))

    def run(self):
        self.step_and_display()
        self.show_welcome()
        while True:
            cmd = get_input()
            if cmd == "exit":
                return
            redisplay = self.handle_input(cmd)
            if redisplay:
                self.step_and_display()
                if self.is_complete():
                    print("ALL SHIFTS ASSIGNED!") # TODO: put this in display_unassigned and rename to display_end_msg
                    self.display_unassigned_people()
                    cmd = get_input(msg="Type 'exit' to end the program; type anything else to continue: ")
                    if cmd == "exit":
                        return
    
    def handle_input(self, x):
        try:
            return self.handle_input_cases(x)
        except InputError as err:
            print(err)
            return ASK_AGAIN

    def handle_input_cases(self, x):
        if x == "help":
            display_help(people, shifts)
            return ASK_AGAIN
        elif x == "show status":
            return REDISPLAY
        elif x == "show rules":
            display_rules(rule_commands)
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
            self.set_autoassign(True)
            return REDISPLAY
        elif x.startswith("assign"):
            self.handle_assignment(x)
            return REDISPLAY
        elif x.startswith("unassign"):
            self.handle_assignment(x)
            return REDISPLAY
        elif x.startswith("remove rule"):
            r = parse_remove_rule(rule_commands, x)
            if r == None:
                continue # go to top of inner while loop and ask for input again
            else:
                if r in shift_person_rules:
                    del shift_person_rules[r]
                else:
                    del person_person_rules[r]
                print("Removing rule %s (%s)" %(r, rule_commands[r]))
                del rule_commands[r]
                break # go to top of outer while loop; recalculate and redisplay everything
        elif x.startswith("show notes"):
            possibilities_by_shift = get_possibilities_by_shift(data, shifts, other_assignments, assignments, shift_person_rules, person_person_rules)
            args = get_args(x)
            if len(args) == 3:
                if is_person_argument(people, args[2]):
                    display_notes(possibilities_by_shift, person=args[2])
                else:
                    print("Unrecognized person %s. Recognized people are : " %args[2], ", ".join(people))
                    print("Could not parse input.")
            else:
                print("Incorrect number of arguments to 'show notes'. Expected 1, got %s : %s" %(len(args - 2), ", ".join(args[2:])))
                print("Could not parse input.")
            continue # go to top of inner while loop and ask for input again
        elif x.startswith("exclude"):
            args = get_args(x)
            r = None
            rule_name = "rule" + str(rule_counter)
            if len(args) == 3 and is_person_argument(people, args[1]):
                if is_person_argument(people, args[2]):
                    r = parse_person_person_rule(data, x)
                    if r != None:
                        person_person_rules[rule_name] = r
                else:
                    r = parse_shift_person_rule(data, x) 
                    if r != None:
                        shift_person_rules[rule_name] = r
                if r == None:
                    print("Could not parse input.")
                    continue # go to top of inner while loop and ask for input again
            else:
                print("Could not parse input.")
                continue # go to top of inner while loop and ask for input again
            rule_counter += 1
            rule_commands[rule_name] = " ".join(args)
            print("Adding rule %s (%s)" %(rule_name, rule_commands[rule_name]))
            break # go to top of outer while loop; recalculate and redisplay everything
        else:
            print("Input not recognized.")
            display_help(people, shifts)

    # check that an input argument does in fact correspond to a person
    def check_person_arg(x):
        if x not in self.people:
            raise InputError("Unrecognized person %s. Recognized people are : " %x, ", ".join(self.people))
 
    # check that an input argument does in fact correspond to a person
    # TODO: make sure exclude has a special thing saying other-shifts are not alloewd
    def check_shift_arg(x):
        if x == "other1" or x == "other2":
            return
        shift_names = [shift_name(s) for s in self.shifts] # XXX: for some reason map doesn't print the error message correctly?
        if x not in shift_names:
            raise InputError("Unrecognized shift %s. Recognized shifts are : %s" %(args[2], ", ".join(list(set(shift_names)))))

    def set_autoassign(value):
        new_status = "on" if value else "off" 
        opposite_status = "off" if value else "on" 
        if autoassign == value:
            print("Well, autoassign is already %s, so...sure?" %new_status)
        else:
            print("Turning autoassignment %s. Write 'autoassign %s' to turn it back %s." %(new_status, opposite_status, opposite_status))
            autoassign = value

    # Expects: assign <person> {<shift>, other1, other2}
    def handle_assignment(self, cmd):
        person, shift = get_args(cmd, "assign", 2)
        check_person_arg(person)
        check_shift_arg(shift)
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
        raise InputError("Could not assign shift; all shifts of type %s are taken. Did you type the correct week?" %args[2])

    # Expects: unassign <person> {<shift>, other1, other2}
    def handle_unassignment(self, cmd):
        person, shift = get_args(cmd, "unassign", 2)
        check_person_arg(person)
        check_shift_arg(shift)
        msg = "Unassigning %s from shift %s" %(person, shift)
        if shift == "other1":
            if person in self.other_assignments[WEEK1]:
                self.other_assignments[WEEK1].remove(person) 
                print(msg)
                return
        elif shift == "other2":
            if person in self.other_assignments[WEEK2]:
                self.other_assignments[WEEK2].remove(person) 
                print(msg)
                return
        else:
            for s in assignments:
                if shift_name(s) == shift and assignments[s] == person:
                    del assignments[s]
                    print(msg)
                    return
        # if we get here, then the person was not assigned to that shift
        raise InputError("Could not unassign %s from shift %s because they are not currently assigned to it." %(person, shift))
        print("Error: %s is not currently assigned to shift %s." %(args[1], args[2]))

    # Expects: remove rule <rule name>
    def handle_remove_rule(self, cmd):
        args = get_args(cmd, "remove rule", 1)
        if len(args) != 3:
            print("Unexpected number of arguments to 'remove rule'! Expected 1 argument but got %s : %s" %(len(args) - 2, ", ".join(args[2:])))
            return None
        if args[2] not in rule_commands:
            print("Unrecognized rule name %s. Recognized rule names are: %s" %(args[2], ", ".join(rule_commands.keys())))
            return None
        return args[2]



# assignments should be a dictionary from shift to person and signify that a person is assigned to that shift 
# shift_person_rules should be a dictionary from a string (name of the rule) to a function from shift -> person -> bool (true if OK, false if this pairing is excluded)
# person_person_rules should be a dictionary from a string (name of the rule) to a function from person -> person -> bool (true if OK, false if this pairing is excluded)
def get_possibilities_by_shift(data, shifts, other_assignments, assignments, shift_person_rules, person_person_rules):
    people = data.keys()

    notes = {p : [] for p in people} # explains reasons for maybes
    warnings = [] # shows preferences violated by current assignment
    possibilities_by_shift = { s : [] for s in shifts}
    assigned = { s : False for s in shifts }
    has_shift_for_week = { week : {p : False for p in people} for week in [WEEK1, WEEK2] }
    remaining_shifts = get_remaining_shifts(data, other_assignments, assignments)

    # first do assignments
    for s in shifts:
        if s in assignments:
            name = assignments[s]
            possibilities_by_shift[s] = [(name, [])]
            has_shift_for_week[s.week][name] = True
            assigned[s] = True
    for week in other_assignments:
        for name in other_assignments[week]:
            has_shift_for_week[week][name] = True

    # next aggregate other possibilities
    for s in shifts:
        if assigned[s]:
            continue
        for p in people:
            if remaining_shifts[p] <= 0 or has_shift_for_week[s.week][p]:
                continue
            answer = get_answer(data, p, s)
            if answer == YES:
                possibilities_by_shift[s].append((p, [])) 
            if answer == MAYBE:
                notes = []
                if data[p][s.time] == MAYBE:
                    notes.append(MAYBE_TIME)
                if s.is_cooking and (data[p][COOK] == MAYBE):
                    notes.append(MAYBE_TYPE)
                    if s.is_big_cooking and (data[p][BIGCOOK] == MAYBE):
                        notes.append(MAYBE_BIGCOOK)
                elif data[p][CLEAN] == MAYBE:
                    notes.append(MAYBE_TYPE)
                possibilities_by_shift[s].append((p, notes))

    # now apply rules
    for rule_okay in shift_person_rules.values():
        for s in shifts:
            possibilities_by_shift[s] = [(p, notes) for p, notes in possibilities_by_shift[s] if rule_okay(s, p)]

    paired_shifts = get_paired_shifts(shifts)
    for rule_okay in person_person_rules.values():
        for s1 in paired_shifts.keys():
            if assigned[s1]:
                p1 = possibilities_by_shift[s1][0][0]
                for s2 in paired_shifts[s1]:
                    possibilities_by_shift[s2] = [(p2, notes) for p2, notes in possibilities_by_shift[s2] if rule_okay(p1, p2)]
    return possibilities_by_shift

# maps each shift to other shifts that occur at the same time (generally there's only one other shift)
def get_paired_shifts(shifts):
    paired_shifts = {s : [] for s in shifts}
    for s1 in shifts:
        for s2 in shifts:
            if s1 == s2:
                continue
            if s1.day == s2.day and s1.week == s2.week and s1.is_cooking == s2.is_cooking:
                paired_shifts[s1].append(s2)
    return paired_shifts

# auto-assigns people if they are the last one who can do a shift
# N.B. does not auto-assign people if they only have one more shift they can do, because if you have more people than shifts that's not an obvious choice
def auto_assign(shifts, people, other_assignments, assignments, possibilities_by_shift):
    paired_shifts = get_paired_shifts(shifts)
    shifts_by_people = get_shifts_by_people(people, assignments, possibilities_by_shift)
    remaining_shifts = get_remaining_shifts(data, other_assignments, assignments)

    # assign people who are the last option for a shift
    for s in shifts:
        if s in assignments:
            continue
        if len(possibilities_by_shift[s]) == 1:
            name = possibilities_by_shift[s][0][0] 
            print("Auto-assigning %s to shift %s because they are the only remaining possibility" %(name, s))
            return (s, name)
        if len(possibilities_by_shift[s]) == 2 and not s.is_cooking: # we don't autoassign cooking shifts because designating the big cook is kind of an important choice
            for s2 in paired_shifts[s]:
                if len(possibilities_by_shift[s2]) == 2:
                    # check if the 2 possibilities are the same people
                    p1 = possibilities_by_shift[s][0][0]
                    p2 = possibilities_by_shift[s][1][0]
                    p3 = possibilities_by_shift[s2][0][0]
                    p4 = possibilities_by_shift[s2][1][0]
                    if (p1 == p3 and p2 == p4) or (p1 == p4 and p2 == p3):
                        # p1 and p2 are the only possibilities for these two shifts; auto-assign them
                        # it is sufficient to auto-assign one, the next round will catch the next one
                        print("Auto-assigning %s to shift %s because they and %s are the only remaining possibilities for two simultaneous shifts" %(p1, s, p2))
                        return (s, p1)

def get_remaining_shifts(data, other_assignments, assignments):
    remaining_shifts = {p : (1 if data[p][FULL_OR_HALF] == HALF else 2) for p in data.keys()}
    for p in assignments.values():
        remaining_shifts[p] -= 1
    for week in other_assignments:
        for p in other_assignments[week]:
            remaining_shifts[p] -= 1
    return remaining_shifts

def make_note(name, shift, maybe_code):
    note = None
    if maybe_code == MAYBE_TYPE:
        note = "%s only 'maybe' wants to do a %s shift" %(name, "cooking" if shift.is_cooking else "cleaning")
    elif maybe_code == MAYBE_TIME:
        note = "%s only 'maybe' is available for %s on %s" %(name, "cooking" if shift.is_cooking else "cleaning", shift.day)
    elif maybe_code == MAYBE_BIGCOOK:
        note = "%s only 'maybe' wants to big cook" %name
    else:
        print("Error: Unrecognized maybe-code %s" %maybe_code)
    return note

def get_warnings(data, shifts, other_assignments, assignments, possibilities_by_shift):
    # TODO: warn when a rule is violated 
    remaining_shifts = get_remaining_shifts(data, other_assignments, assignments)
    has_shift_for_week = { week : {p : False for p in data.keys()} for week in [WEEK1, WEEK2] }
    warnings = []
    
    for s, p in assignments.items():
        # warn if someone is doing multiple shifts in the same week
        if has_shift_for_week[s.week][p]:
            warnings.append("%p has multiple shifts in the same week (week %s)" %(p, s.week))
        has_shift_for_week[s.week][p] = True
        
        # warn if someone is doing too many shifts
        if remaining_shifts[p] < 0:
            warnings.append("%p is doing too many shifts" %p)
        
        # warn if someone is assigned to a thing they said no to
        if get_answer(data, p, s) == NO:
            if data[p][s.time] == NO:
                warnings.append("%s is assigned to shift %s even though they said they are unavailable" %(p, s))
            if data[p][COOK] == NO and s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cooking" %(p, s))
            if data[p][CLEAN] == NO and not s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cleaning" %(p, s))
            if data[p][BIGCOOK] == NO and not s.is_big_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to big cooking" %(p, s))

    # warn if no one is available for a shift
    for s, possibilities in possibilities_by_shift.items():
        if len(possibilities) == 0:
            warnings.append("No one is available for shift %s" %s)
    return warnings

# mapping from each person to all unassigned shifts that they could work
def get_shifts_by_people(people, assignments, possibilities_by_shift):
    shifts_by_people = {p : [] for p in people}
    for s in possibilities_by_shift:
        if s in assignments:
            continue
        for p, _ in possibilities_by_shift[s]:
            shifts_by_people[p].append(s)
    return shifts_by_people

def get_suggestions(data, shifts, other_assignments, assignments, possibilities_by_shift):
    people = list(data.keys())
    paired_shifts = get_paired_shifts(shifts)
    shifts_by_people = get_shifts_by_people(people, assignments, possibilities_by_shift)
    remaining_shifts = get_remaining_shifts(data, other_assignments, assignments)
    available_people = list(filter(lambda p : remaining_shifts[p] > 0, people))
    suggestions = [] 

    # suggest pairing people who want to work together
    for p1 in available_people:
        for p2 in data[p1][PAIR]:
            for s1 in shifts_by_people[p1]:
                for s2 in paired_shifts[s1]: 
                    if s2 in assignments and assignments[s2] == p2:
                        justification = "so %s and %s can work together as requested by %s" %(p1, p2, p1)
                        if p1 in data[p2][PAIR]:
                            justification += " and %s both" %p2
                        suggestions.append(("assign %s %s" %(p1, s1), justification))

    # suggest new people for non-cleaning shifts if they preferred that
    for p in available_people:
        if data[p][NEW]:
            if data[p][COOK] == YES or (data[p][COOK] == MAYBE and data[p][CLEAN] == MAYBE):
                # they consider cooking better or equal, and could have both types available
                available_cooking_shifts = list(filter(lambda s : shift.is_cooking, shifts_by_people[p]))
                available_cleaning_shifts = list(filter(lambda s : not shift.is_cooking, shifts_by_people[p]))
                if len(available_cleaning_shifts) == 0:
                    continue # if they can't do any cleaning shifts anyway, then there's no suggestion to make
                for s in available_cooking_shifts:
                    suggestions.append(("assign %s %s" %(p, s), "because new people tend to be far happier (and less likely to drop) on cooking shifts if they requested that"))

    # if there's only one person left without a 'maybe' answer on a particular shift, suggest them
    for s in possibilities_by_shift:
        if s in assignments:
            continue
        yes_people = list(filter(lambda x : len(x[1]) == 0, possibilities_by_shift[s]))
        if len(yes_people) == 1:
            suggestions.append(("assign %s %s" %(yes_people[0][0], s), "because they are the only remaining person who said 'yes' to all the shift's availability/shift-type questions")) 

    # if a person only has one shift left that they have no 'maybes' for, suggest it
    for p in available_people:
        yes_shifts = []
        for s in shifts_by_people[p]:
            notes = list(filter(lambda x: x[0] == p, possibilities_by_shift[s]))[0][1]
            if len(notes) == 0:
                yes_shifts.append(s)
        if len(yes_shifts) == 1 and yes_shifts[0] not in assignments:
            suggestions.append(("assign %s %s" %(p, yes_shifts[0]), "because this is the only remaining shift for which they said 'yes' to all the availability/shift-type questions")) 

    suggestions_reformatted = {}
    for cmd, justification in suggestions:
        if cmd in suggestions_reformatted:
            suggestions_reformatted[cmd].append(justification)
        else:
            suggestions_reformatted[cmd] = [justification]

    return suggestions_reformatted

def display_notes(possibilities_by_shift, person=None):
    notes = []
    for s in possibilities_by_shift:
        for p, maybe_notes in possibilities_by_shift[s]:
            if person == None or person == p:
                for n in maybe_notes:
                    notes.append(make_note(p, s, n))
    
    print("Notes:")
    notes = list(set(notes))
    notes.sort()
    for n in notes:
        print("\t- " + n)

def display_suggestions(suggestions):
    print("Suggested moves:")
    for cmd, justifications in suggestions.items():
        print("\t-%s (%s)" %(cmd, " and ".join(justifications)))
    if len(suggestions) == 0:
        print("\t No suggestions, sorry!")


def display_state(shifts, other_assignments, possibilities_by_shift, warnings):
    table = {s : [] for s in shifts}
    notes = []
    
    for s in possibilities_by_shift:
        for p, maybe_notes in possibilities_by_shift[s]:
            display_p = p
            for n in maybe_notes:
                display_p = "(" + display_p + ")"
                notes.append(make_note(p, s, n))
            table[s].append(display_p)
    
    week = None
    day = None
    for s in shifts:
        if s.week != week:
            print("")
            print("Week %s" %s.week)
            print("======")
            print("other%s: %s" %(s.week, ", ".join(other_assignments[s.week])))
            print("")
        elif s.day != day:
            print("")
        day = s.day
        week = s.week
        print("%s : %s" %(s, "; ".join(sorted(table[s], reverse=True)))) 

    print("")
    for warning in warnings:
        print("WARNING: %s" %warning)

    return None

def step_and_display(data, shifts, other_assignments, assignments, shift_person_rules, person_person_rules, autoassign=True):
    possibilities_by_shift = get_possibilities_by_shift(data, shifts, other_assignments, assignments, shift_person_rules, person_person_rules)
    people = list(data.keys())
    new_assignment = None
    if autoassign:
        new_assignment = auto_assign(shifts, people, other_assignments, assignments, possibilities_by_shift)

    # repeat adding new assignments and recalculating until no one else can be automatically assigned
    while new_assignment != None:
        s, name = new_assignment
        assignments[s] = name
        possibilities_by_shift = get_possibilities_by_shift(data, shifts, other_assignments, assignments, shift_person_rules, person_person_rules)
        new_assignment = auto_assign(shifts, people, other_assignments, assignments, possibilities_by_shift)

    display_state(shifts, other_assignments, possibilities_by_shift, get_warnings(data, shifts, other_assignments, assignments, possibilities_by_shift))

    return assignments

def is_complete(shifts, assignments):
    unfilled = [s for s in shifts if s not in assignments]
    return len(unfilled) == 0

def display_rules(rule_commands):
    for r in (sorted(rule_commands.keys())):
        print("%s : %s" %(r, rule_commands[r]))
    if len(rule_commands) == 0:
        print("No rules yet!")

def display_assignments(shifts, assignments):
    for s in shifts:
        if s in assignments:
            print("%s : %s" %(s, assignments[s]))
    if len(assignments) == 0:
        print("No assignments yet!")

def shift_name(s):
    return str(s).lower()
    
def display_tips():
    print(" - If a name has parentheses, that means the person answered 'maybe' to questions about that shift time/type")
    print(" - To see details about 'maybe' answers, type 'show notes' or 'show notes <person's name>'")
    print(" - The 'other' category is for miscellaneous shifts, like tiny cook, fridge ninja, or brunch cook")
    print(" - Type 'show suggestions' to get suggestions for next moves")

def display_help(people, shifts):
    print("Tips:")
    display_tips()
    print("")
    print("Possible commands (everything is case-insensitive):")
    print("\texit\t\t- close program")
    print("\tshow status\t\t- display the current state of assignments/possibilities")
    print("\tshow rules\t\t- display the rules currently in effect")
    print("\tshow notes\t\t- display the reasons for any 'maybe' parentheses currently displayed")
    print("\tshow notes <person>\t- display the reasons for any 'maybe' parentheses currently displayed around <person>")
    print("\tshow assignments\t- display the shift assignments currently in effect")
    print("\tshow suggestions\t- suggest next moves")
    print("\tautoassign off\t\t- turn off autoassign (on by default), which is when the system automatically identifies and fills shifts that can only be filled one way")
    print("\tautoassign on\t\t- turn autoassign back on")
    print("\tremove rule <rule name>\t- remove a rule based on the name shown by 'show rules'")
    print("\tassign <person> <shift>\t- assign <person> to <shift> (e.g. 'assign %s %s')" %(people[0], shift_name(shifts[0])))
    print("\tassign <person> other\t- assign <person> to some shift that doesn't appear here (e.g. fridge ninja or tiny cook), so that they don't show up as possibilities for other shifts")
    print("\tunassign <person> <shift>\t- unassign <person> from <shift>")
    print("\texclude <person> <shift_type>\t- exclude <person> from certain shift types ('%s',' %s', or '%s')" %tuple(SHIFT_TYPES))
    print("\texclude new <shift_type>\t- exclude all people new to mealplan from certain shift types ('%s', '%s', or '%s')" %tuple(SHIFT_TYPES))
    print("\texclude <person> <shift>\t- exclude <person> from a certain shift (e.g. '%s' or '%s')" %(shift_name(shifts[0]), shift_name(shifts[3])))
    print("\texclude new <shift>\t\t- exclude all people new to mealplan from a certain shift (e.g. '%s' or '%s')" %(shift_name(shifts[0]), shift_name(shifts[3])))
    print("\texclude <person> <person>\t- exclude two people from working together") 
    print("\texclude new <person>\t- exclude someone from working with new people") 
    print("\texclude new new\t\t- exclude possibilities where two people who are *both* new to mealplan would work together") 

def get_args(cmd):
    return [a.strip() for a in (cmd.strip().split(" ")) if a.strip() != ""]

def parse_person_person_rule(data, cmd):
    args = get_args(cmd)
    if len(args) != 3:
        print("Unexpected number of arguments to 'exclude'! Expected 2 arguments but got %s : %s" %(len(args) - 1, ", ".join(args[1:])))
        return None
    for a in args[1:]:
        if a not in data and a != "new":
            print("Unrecognized person %s. Recognized people are : %s" %(args[1], ", ".join(people)))
            return None
    if args[1] == "new":
        if args[2] == "new":
            return (lambda p1, p2: not (data[p1][NEW] and data[p2][NEW])) # excludes new people from working together
        else:
            return (lambda p1, p2 : not ((data[p1][NEW] and p2 == args[2]) or (p1 == args[2] and data[p2][NEW])))
    else:
        if args[2] == "new":
            return (lambda p1, p2 : not ((data[p1][NEW] and p2 == args[1]) or (p1 == args[1] and data[p2][NEW])))
        else:
            if args[1] == args[2]:
                print("You cannot exclude someone from cooking with themselves. What's your problem?")
                return None
            return (lambda p1, p2 : not (p1 == args[1] and p2 == args[2]) or (p1 == args[2] and p2 == args[2]))

def parse_shift_person_rule(data, cmd):
    args = get_args(cmd)
    if len(args) != 3:
        print("Unexpected number of arguments to 'exclude'! Expected 2 arguments but got %s : %s" %(len(args) - 1, ", ".join(args[1:])))
        return None
    if args[1] not in data and args[1] != "new":
        print("Unrecognized person %s. Recognized people are : " %(args[1], ", ".join(people)))
        return None

    if args[2] in SHIFT_TYPES:
        if args[1] == "new":
            return (lambda s, p : not (s.type == args[2] and data[p][NEW]))
        else:
            return (lambda s, p : not (s.type == args[2] and p == args[1]))
    else: # args[2] must be a specific shift
        shift_names = map(shift_name, shifts)
        if args[2] not in shift_names:
            print("Unrecognized shift %s. Recognized shifts are : %s" %(args[2], ", ".join(list(set(shift_names)))))
            return None
        if args[1] == "new":
            return (lambda s, p : not (shift_name(s) == args[2] and data[p][NEW]))
        else:
            return (lambda s, p : not (shift_name(s) == args[2] and p == args[1]))

def is_person_argument(people, x):
    if x == "new":
        return True
    if x in people:
        return True
    return False

def display_unassigned_people(data, other_assignments, assignments):
    remaining_shifts = get_remaining_shifts(data, other_assignments, assignments)
    nonzero_remaining_shifts = {p : rem for p, rem in remaining_shifts.items() if rem != 0}
    if len(nonzero_remaining_shifts) != 0:
        print("Some people have remaining shifts (they can be assigned as tiny cooks etc):")
        for p, rem in remaining_shifts.items():
            if rem != 0:
                print("%s : %s shifts remaining" %(p, rem))

def display_welcome():
    print("**** Welcome to the Kitchen Scheduler 1000! ****")
    display_tips()
    print(" - To show all possible commands, type 'help'") # this tip is separate so it doesn't show up in the help message, that would be dumb
    print("")


def get_answer(data, name, shift):
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
    do_schedule(data)
    # TODO: better error handling -- maybe fail to do the step in some cases, in others just allow showing no possibilities?
    # TODO: save/load functionality
    # TODO: add heuristic/brute force search at some point?

