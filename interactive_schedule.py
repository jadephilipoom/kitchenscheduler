import sys, csv, cmd

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
    
def get_notes(data, p, s):
    notes = []
    if data[p][s.time] == MAYBE:
        notes.append(MAYBE_TIME)
    if s.is_cooking and (data[p][COOK] == MAYBE):
        notes.append(MAYBE_TYPE)
        if s.is_big_cooking and (data[p][BIGCOOK] == MAYBE):
            notes.append(MAYBE_BIGCOOK)
    elif data[p][CLEAN] == MAYBE:
        notes.append(MAYBE_TYPE)
    return notes

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

# returns true if person p strictly prefers cleaning to cooking 
def prefers_cleaning(data, p):
    cook = data[p][COOK]
    clean = data[p][CLEAN]
    if cook == YES: return False
    if cook == NO: return True
    if cook == MAYBE: return (clean == NO)


# The schedule state. Can be modified by:
# - assignment
# - unassignment
# - rule additions
# - autoassign toggle
#
# Provides the following information:
# - possibile people by shift
# - # remaining shifts by person
# - next rule name
#
# Note: although 'other' is treated special internally, it should be treated as just another shift name in the API
class Schedule:
    shifts = generate_shifts()

    def __init__(self, data):
        self.data = data
        self.people = list(data.keys())
        self.paired_shifts = {s1 : [s2 for s2 in self.shifts if Shift.paired(s1, s2)] for s1 in self.shifts}
        self.shift_person_rules = {}  # dictionary mapping rule name (string) to a function with type person -> shift -> bool (true if OK, false if this pairing is excluded)
        self.person_person_rules = {} # dictionary mapping rule name (string) to a function with type person -> person -> bool (true if OK, false if this pairing is excluded)
        self.rule_commands = {}
        self.rule_counter = 0
        self.other_assignments = {"other1" : [], "other2" : []}
        self.assignments = {} # dictionary mapping shift to person and signify that a person is assigned to that shift 
        self.autoassign = True

    def is_person(self, p):
        return p in self.people
    
    def is_shift_name(self, s):
        return (s in self.other_assignments) or (s in map(shift_name, self.shifts))

    def has_shift(self, p, shiftname):
        return any(map(lambda s: shift_name(s) == shiftname, self.get_current_shifts(p)))
    
    def has_shift_for_week(self, p, week):
        for s in self.get_current_shifts(p):
            if s.week == week:
                return True
    
    def get_current_shifts(self, p):
        shifts = [s for s, p2 in self.assignments.items() if p == p2]
        return shifts + [s for s, people in self.other_assignments.items() if p in people]
    
    def get_possible_shifts(self, p):
        possibilities_by_shift = self.get_possibilities_by_shift()
        return list(filter(lambda s : p in possibilities_by_shift[s], self.get_unassigned_shifts()))

    def get_unassigned_shifts(self):
        return [s for s in Schedule.shifts if s not in self.assignments]

    def rules_broken(self, p, s):
        out = [r for r, rule_okay in self.shift_person_rules.items() if not rule_okay(p, s)]
        for r, rule_okay in self.person_person_rules.items():
            for s2 in self.paired_shifts[s]:
                if s2 in self.assignments and not rule_okay(p, self.assignments[s2]):
                    out.append(r)
        return out

    def is_complete(self):
        return all([s in self.assignments for s in self.shifts])
    
    def get_other(self, week):
        if week == WEEK1:
            return self.other_assignments["other1"]
        elif week == WEEK2:
            return self.other_assignments["other2"]
        else:
            raise Exception("Unrecognized week %s (expected %s or %s)" %(week, WEEK1, WEEK2))

    def get_notes(self, person=None):
        notes = []
        for s, options in self.get_possibilities_by_shift().items():
            for p, maybe_notes in options:
                if person == None or person == p:
                    notes.extend(map(lambda n : make_note(p, s, n), maybe_notes))
        return list(set(notes))

    def set_autoassign(self, value):
        new_status = "on" if value else "off" 
        opposite_status = "off" if value else "on" 
        if self.autoassign == value:
            print("Well, autoassign is already %s, so...sure?" %new_status)
        else:
            print("Turning autoassignment %s. Write 'autoassign %s' to turn it back %s." %(new_status, opposite_status, opposite_status))
            self.autoassign = value

    def assign(self, person, shift):
        if shift == "other1" or shift == "other2":
            self.other_assignments[shift].append(person)
            return
        else:
            for s in self.get_unassigned_shifts():
                if shift_name(s) == shift:
                    self.assignments[s] = person
                    return
        # if we get here, then no shifts were unclaimed
        raise InputError("Could not assign shift; all shifts of type %s are taken. Did you type the correct week?" %shift)

    def unassign(self, person, shiftname):
        if shiftname == "other1" or shiftname == "other2":
            self.other_assignments[shiftname].remove(person)
        else:
            to_unassign = list(filter(lambda s: shift_name(s) == shiftname, self.get_current_shifts(person)))
            if len(to_unassign) == 0:
                raise Exception("%s is not assigned to shift %s" %(person, shift))
            for shift in to_unassign:
                del self.assignments[shift]
        
    def remove_rule(self, r):
        if r not in self.rule_commands:
            raise InputError("Unrecognized rule name %s. Recognized rule names are: %s" %(r, ", ".join(self.rule_commands.keys())))
        if r in self.shift_person_rules:
            del self.shift_person_rules[r]
        else:
            del self.person_person_rules[r]
        del self.rule_commands[r]

    def next_rule_name(self):
        return "rule" + str(self.rule_counter)

    def add_person_person_rule(self, p1, p2):
        if p1 == p2 and p1 != "new":
            raise InputError("You cannot exclude someone from cooking with themselves. What's your problem?")
        cond1 = lambda p : p == p1
        cond2 = lambda p : p == p2
        if p1 == "new":
            cond1 = lambda p : self.data[p][NEW]
        if p2 == "new":
            cond2 = lambda p : self.data[p][NEW]
        rule_name = self.next_rule_name()
        self.person_person_rules[rule_name] = lambda px, py : not ((cond1(px) and cond2(py)) or (cond2(px) and cond1(py)))
        self.rule_counter += 1
        self.rule_commands[rule_name] = "exclude %s %s" %(p1, p2)

    def add_shift_person_rule(self, p1, x):
        cond1 = lambda p : p == p1
        cond2 = lambda s : shift_name(s) == x
        if p1 == "new":
            cond1 = lambda p : self.data[p][NEW]
        if x in SHIFT_TYPES:
            cond2 = lambda s : s.type == x
        rule_name = self.next_rule_name()
        self.shift_person_rules[rule_name] = lambda p, s : not (cond1(p) and cond2(s))
        self.rule_counter += 1
        self.rule_commands[rule_name] = "exclude %s %s" %(p1, x)

    def get_remaining_shifts(self):
        remaining_shifts = {p : (1 if self.data[p][FULL_OR_HALF] == HALF else 2) for p in self.people}
        for p in self.assignments.values():
            remaining_shifts[p] -= 1
        for week in self.other_assignments:
            for p in self.other_assignments[week]:
                remaining_shifts[p] -= 1
        return remaining_shifts

    def get_warnings(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        remaining_shifts = self.get_remaining_shifts()
        warnings = []
        for s, p in self.assignments.items():
            if remaining_shifts[p] < 0:
                warnings.append("%s is doing too many shifts" %p)
            if self.data[p][s.time] == NO:
                warnings.append("%s is assigned to shift %s even though they said they are unavailable" %(p, s))
            if self.data[p][COOK] == NO and s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cooking" %(p, s))
            if self.data[p][CLEAN] == NO and not s.is_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to cleaning" %(p, s))
            if self.data[p][BIGCOOK] == NO and s.is_big_cooking:
                warnings.append("%s is assigned to shift %s even though they said no to big cooking" %(p, s))
            warnings.extend(map(lambda rule_name : "%s is assigned to shift %s even though this breaks %s (%s)" %(p, s, rule_name, self.rule_commands[rule_name]), self.rules_broken(p, s)))
        for p in self.people:
            for week in [WEEK1, WEEK2]:
                shifts = list(filter(lambda s : s.week == WEEK1, self.get_current_shifts(p)))
                if len(shifts) > 1:
                    warnings.append("%s has multiple shifts in the same week (week %s)" %(p, week))
        for s, possibilities in possibilities_by_shift.items():
            if len(possibilities) == 0:
                warnings.append("No one is available for shift %s" %s)
        warnings.sort()
        return list(set(warnings))

    # mapping from each person to all unassigned shifts that they could work
    def get_shifts_by_people(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        shifts_by_people = {p : [] for p in self.people}
        for s in self.get_unassigned_shifts():
            for p, _ in possibilities_by_shift[s]:
                shifts_by_people[p].append(s)
        return shifts_by_people

    def suggest_pairings(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        out = []
        for s1 in Schedule.shifts:
            for s2 in self.paired_shifts[s1]:
                for p1, _ in possibilities_by_shift[s1]:
                    for p2 in filter(lambda p : p in self.data[p1][PAIR], possibilities_by_shift[s2]):
                        justification = "so %s and %s can work together as requested by %s" %(p1, p2, p1)
                        if p1 in self.data[self.assignments[s2]][PAIR]:
                            justification += " and %s both" %self.assignments[s2]
                        out.append((p1, s1, justification))
        return out

    def suggest_new_cook(self):
        shifts_by_people = self.get_shifts_by_people()
        new_people = [p for p, n in self.get_remaining_shifts().items() if n > 0 and self.data[p][NEW] and prefers_cleaning(self.data, p)]
        out = []
        for p in new_people:
            available_cooking_shifts = list(filter(lambda s : s.is_cooking, shifts_by_people[p]))
            available_cleaning_shifts = list(filter(lambda s : not s.is_cooking, shifts_by_people[p]))
            if len(available_cleaning_shifts) != 0: # if they can't do any cleaning shifts anyway, then there's no suggestion to make
                for s in available_cooking_shifts:
                    out.append((p, s, "new people should cook if possible"))
        return out

    def suggest_last_yes(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        out = []
        for s in self.get_unassigned_shifts():
            yes_people = list(filter(lambda x : len(x[1]) == 0, possibilities_by_shift[s]))
            if len(yes_people) == 1:
                out.append((yes_people[0][0], s, "they are the only person with no hesitations about this shift time/type")) 
        return out

    def get_suggestions(self):
        suggestions = []
        suggestions.extend(self.suggest_pairings())
        suggestions.extend(self.suggest_new_cook())
        suggestions.extend(self.suggest_last_yes())

        suggested_shifts_by_person = {p : [] for p in self.people}
        justifications = {(p,s) : [] for p,s,_ in suggestions}
        for person, shift, justification in suggestions:
            suggested_shifts_by_person[person].append(shift)
            justifications[(person, shift)].append(justification)

        multiple_reasons = []
        groups = {}
        for p, shifts in suggested_shifts_by_person.items():
            for s in shifts:
                j = justifications[(p,s)]
                if len(j) > 1:
                    multiple_reasons.append((p,s,j))
                elif len(j) == 1:
                    if (p,j[0]) not in groups:
                        groups[(p,j[0])] = []
                    groups[(p,j[0])].append(s)
        
        multiple_reasons = sorted(list(map(lambda x: ("assign %s %s" %(x[0], x[1]), " and ".join(x[2])), set(multiple_reasons))))
        groups = sorted(list(map(lambda x : ("assign %s %s" %(x[0][0], " or ".join(set(map(str, x[1])))), x[0][1]), groups.items())))

        return multiple_reasons + groups 

    def get_possibilities_by_shift(self):
        possibilities_by_shift = { s : [] for s in self.get_unassigned_shifts()}
        available_people = [p for p, n in self.get_remaining_shifts().items() if n > 0]
        for s in self.get_unassigned_shifts():
            for p in available_people:
                if get_answer(self.data, p, s) != NO and not self.has_shift_for_week(p, s.week) and not self.rules_broken(p, s):
                    possibilities_by_shift[s].append((p, get_notes(self.data, p, s)))
        return possibilities_by_shift

    # auto-assigns people if they are the last one who can do a shift
    def auto_assign_one(self):
        possibilities_by_shift = self.get_possibilities_by_shift()
        for s in self.get_unassigned_shifts():
            options = possibilities_by_shift[s]
            if len(options) == 1:
                name = options[0][0] 
                print("Auto-assigning %s to shift %s because they are the only remaining possibility" %(name, s))
                return (s, name)
            if len(options) == 2 and not s.is_cooking: # don't autoassign cooking shifts because designating the big cook is kind of an important choice
                for s2 in self.paired_shifts[s]:
                    if len(possibilities_by_shift[s2]) == 2:
                        if all(map(lambda p : p in possibilities_by_shift[s2], options)) and all(map(lambda p : p in options, possibilities_by_shift[s2])):
                            print("Auto-assigning %s to shift %s because they and %s are the only remaining possibilities for two simultaneous shifts" %(options[0][0], s, options[1][0]))
                            return (s, options[0][0]) # it is sufficient to auto-assign one, the next round will catch the next one

    def auto_assign(self):
        if not self.autoassign:
            return None
        new_assignment = self.auto_assign_one()
        # repeat adding new assignments and recalculating until no one else can be automatically assigned
        while new_assignment != None:
            s, name = new_assignment
            self.assignments[s] = name
            new_assignment = self.auto_assign_one() 

class Loop(cmd.Cmd):
    prompt = "Enter your move (type '?' or 'help' for options): "
    file=None
    # number of arguments expected by each command
    nargs = {
            "autoassign": [1],
            "exit" : [0],
            "show" : [1, 2],
            "assign" : [2],
            "unassign": [2],
            "exclude" : [2],
            "remove" : [2] }

    def __init__(self, data):
        super().__init__()
        self.state = Schedule(data)
        self.redisplay = False # flag used to indicate whether status should be redisplayed 
    
    def tips():
        lines = []
        lines.append(" - Parentheses around a name indicate they only 'maybe' want that shift time/type; type 'show notes <person's name>' for details")
        lines.append(" - The 'other' category is for miscellaneous shifts, like tiny cook, fridge ninja, or brunch cook")
        lines.append(" - Type 'show suggestions' to get suggestions for next moves")
        return "\n".join(lines)
    
    def welcome():
        lines = []
        lines.append("**** Welcome to the Kitchen Scheduler 1000! ****")
        lines.append(" - Type 'show status' to see the current possibilities for each shift, based on the input data")
        lines.append(Loop.tips())
        lines.append("")
        return "\n".join(lines)
    
    def commands():
        lines = []
        lines.append("Possible commands (everything is case-insensitive):")
        lines.append("\texit\t\t- close program")
        lines.append("\tshow status\t\t- display the current state of assignments/possibilities")
        lines.append("\tshow rules\t\t- display the rules currently in effect")
        lines.append("\tshow notes\t\t- display the reasons for any 'maybe' parentheses currently displayed")
        lines.append("\tshow notes <person>\t- display the reasons for any 'maybe' parentheses currently displayed around <person>")
        lines.append("\tshow assignments\t- display the shift assignments currently in effect")
        lines.append("\tshow suggestions\t- suggest next moves")
        lines.append("\tassign <person> <shift>\t- assign <person> to <shift> (e.g. 'assign joe %s')" %Schedule.shifts[0])
        lines.append("\tassign <person> other\t- assign <person> to some shift that doesn't appear here (e.g. fridge ninja or tiny cook), so that they don't show up as possibilities for other shifts")
        lines.append("\tunassign <person> <shift>\t- unassign <person> from <shift>")
        lines.append("\tautoassign off\t\t- turn off autoassign (on by default), which is when the system automatically identifies and fills shifts that can only be filled one way")
        lines.append("\tautoassign on\t\t- turn autoassign back on")
        lines.append("\texclude <person> <shift_type>\t- exclude <person> from certain shift types ('%s',' %s', or '%s')" %tuple(SHIFT_TYPES))
        lines.append("\texclude new <shift_type>\t- exclude all people new to mealplan from certain shift types ('%s', '%s', or '%s')" %tuple(SHIFT_TYPES))
        lines.append("\texclude <person> <shift>\t- exclude <person> from a certain shift (e.g. '%s' or '%s')" %(shift_name(Schedule.shifts[0]), shift_name(Schedule.shifts[3])))
        lines.append("\texclude new <shift>\t\t- exclude all people new to mealplan from a certain shift (e.g. '%s' or '%s')" %(shift_name(Schedule.shifts[0]), shift_name(Schedule.shifts[3])))
        lines.append("\texclude <person> <person>\t- exclude two people from working together") 
        lines.append("\texclude new <person>\t- exclude someone from working with new people") 
        lines.append("\texclude new new\t\t- exclude possibilities where two people who are *both* new to mealplan would work together") 
        lines.append("\tremove rule <rule name>\t- remove a rule based on the name shown by 'show rules'")
        return "\n".join(lines)

    #TODO
    '''
    def complete_show(self):
    def complete_assign(self):
    def complete_unassign(self):
    def complete_autoassign(self):
    def complete_exclude(self):
    def complete_remove(self):
    '''

    def postcmd(self, stop, line):
        if self.redisplay:
            self.display_status()
            self.redisplay = False
        if self.state.is_complete():
            self.display_complete()
            x = input("Type 'exit' to end the program; type anything else to continue: ")
            if x == "exit":
                return True
        return stop

    def emptyline(self):
        pass # do nothing on empty input; overrides default Cmd behavior

    def parseline(self, line):
        cmd, arg, line = super().parseline(line)
        args = [a.strip().lower() for a in arg.split(" ") if a.strip() != ""]
        if cmd in self.nargs and len(args) not in self.nargs[cmd]:
            print("Unexpected number of arguments to '%s'! Expected %s, got %s : %s" %(cmd, " or ".join(nargs[cmd]), len(args), ", ".join(args)))
        return cmd, args, line

    def check_person_arg(self, x, new_ok=False):
        if (new_ok and x == "new") or self.state.is_person(x):
            return True
        print ("Unrecognized person %s. Recognized people are : %s" %(x, ", ".join(self.state.people)))
        return False
 
    def check_shift_arg(self, x):
        shift_names = [shift_name(s) for s in Schedule.shifts]
        if self.state.is_shift_name(x):
            return True
        else:
            print("Unrecognized shift %s. Recognized shifts are : %s" %(x, ", ".join(list(set(shift_names)))))
            return False
    
    def do_exit(self, args):
        print("Goodbye!")
        return True
    
    def do_autoassign(self, args):
        if args[0] == "on":
            if not self.state.autoassign:
                self.redisplay = True # only redisplay if we are newly turning autoassign on
            self.state.set_autoassign(True)
        elif args[0] == "off":
            self.state.set_autoassign(False)
        else:
            self.default("autoassign" + args)
    
    def do_assign(self, args):
        person, shift = args
        if not self.check_person_arg(person): return
        # check for case in which we assign someone to e.g. 'bigcookmon' and they get assigned to both weeks at once; treat as though it's two commands
        if self.state.is_shift_name(shift + "1"):
            self.do_assign([person, shift + "1"])
            self.do_assign([person, shift + "2"])
            return
        if not self.check_shift_arg(shift): return
        print("Assigning %s to shift %s" %(person, shift))
        self.state.assign(person, shift)
        self.redisplay = True

    def do_unassign(self, args):
        person, shift = args
        if not self.check_person_arg(person): return
        if self.state.is_shift_name(shift + "1"):
            self.do_unassign([person, shift + "1"])
            self.do_unassign([person, shift + "2"])
            return
        if not self.check_shift_arg(shift): return
        if not self.state.has_shift(person, shift):
            print("%s is not currently assigned to shift %s. Did you type the right week?" %(person, shift))
            return
        print("Unassigning %s from shift %s" %(person, shift))
        self.state.unassign(person, shift)
        self.redisplay = True
    
    def do_remove(self, args):
        rule, r = args
        if not rule == "rule":
            self.default("remove " + " ".join(args))
            return
        print("Removing rule %s (%s)" %(r, self.rule_commands[r]))
        self.state.remove_rule(r)
        self.redisplay = True
 
    def do_exclude(self, args):
        p1, x = args
        if not self.check_person_arg(p1, new_ok=True): return
        print("Adding rule %s (%s). Type 'show rules' to view all rules." %(self.state.next_rule_name(), " ".join(["exclude", p1, x])))
        if self.state.is_shift_name(x) or x in SHIFT_TYPES: 
            self.state.add_shift_person_rule(p1, x)
        elif x == "other":
            print("'other' shifts cannot be used in 'exclude', and there's no reason to do it anyway, so stoppit")
            return
        else:
            if not self.check_person_arg(x, new_ok=True): return
            self.state.add_person_person_rule(p1, x)
        self.redisplay = True

    def do_show(self, args):
        line = "show " + " ".join(args)
        if len(args) == 1:
            arg = args[0]
            if arg == "status":
                self.display_status()
            elif arg == "rules":
                self.display_rules()
            elif arg == "assignments":
                self.display_assignments()
            elif arg == "suggestions":
                self.display_suggestions()
            elif arg == "notes":
                self.display_notes()
            else:
                self.default(line)
        elif len(args) == 2 and args[0] == "notes":
            notes, person = args 
            if not self.check_person_arg(person, new_ok=True): return
            self.display_notes(person)
        else:
            self.default(line)
    
    def do_help(self, args):
        print("Tips:")
        print(Loop.tips())
        print("")
        print(Loop.commands())

    def display_notes(self, person=None):
        notes = self.state.get_notes(person)
        notes.sort()
        print("Notes:")
        for n in notes:
            print("\t- " + n)

    def display_complete(self):
        print("ALL SHIFTS ASSIGNED!")
        remaining_shifts = self.state.get_remaining_shifts()
        nonzero_remaining_shifts = {p : rem for p, rem in remaining_shifts.items() if rem != 0}
        if len(nonzero_remaining_shifts) != 0:
            print("Some people have remaining shifts (they can be assigned as tiny cooks etc):")
            for p, rem in remaining_shifts.items():
                if rem != 0:
                    print("%s : %s shifts remaining" %(p, rem))

    def display_suggestions(self):
        suggestions = self.state.get_suggestions()
        print("Suggested moves:")
        for cmd, justifications in suggestions:
            print("\t-%s (%s)" %(cmd, justifications))
        if len(suggestions) == 0:
            print("\t No suggestions, sorry!")

    def display_rules(self):
        for r in (sorted(self.state.rule_commands.keys())):
            print("%s : %s" %(r, self.state.rule_commands[r]))
        if len(self.state.rule_commands) == 0:
            print("No rules yet!")

    def display_assignments(self):
        for s in self.state.assignments:
            print("%s : %s" %(s, self.state.assignments[s]))
        if len(self.state.assignments) == 0:
            print("No assignments yet!")

    def display_warnings(self):
        print("")
        for warning in self.state.get_warnings():
            print("WARNING: %s" %warning)

    def display_status(self):
        table = {shift_name(s) : [] for s in Schedule.shifts}
        possibilities_by_shift = self.state.get_possibilities_by_shift()
        for s in Schedule.shifts:
            if s in self.state.assignments:
                table[shift_name(s)].append((0, "[%s]" %self.state.assignments[s]))
            else:
                for p, notes in possibilities_by_shift[s]:
                    n = len(notes)
                    table[shift_name(s)].append((n, ("(" * n) + p + (")" * n)))
        for c in table:
            table[c] = sorted(list(set(table[c]))) # remove duplicate entries for cleaning shifts
            table[c] = list(map(lambda x : x[1], table[c]))

        week, day = None, None
        already_printed = []
        for s in Schedule.shifts:
            if s.week != week:
                print("\nWeek %s\n======" %s.week)
                print("other%s: %s\n" %(s.week, ", ".join(self.state.get_other(s.week))))
            elif s.day != day:
                print("")
            week, day = s.week, s.day
            if shift_name(s) not in already_printed:
                print("%s : %s" %(s, "; ".join(table[shift_name(s)]))) 
                already_printed.append(shift_name(s))
        self.display_warnings()


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
    Loop(data).cmdloop(intro=Loop.welcome())
    # TODO: save/load functionality
    # TODO: add heuristic/brute force search at some point?
    # when you unassign someone for a shift, but they were the last person available and said all-yes, they still show up as if they are assigned because the format is ambiguous here. Is this an issue? 

# Questions
# What would be a good output format? Assignments or schedule or csv?
# save/load functionality?

# TODO: right now, making a rule unassigns people. We don't want that.
