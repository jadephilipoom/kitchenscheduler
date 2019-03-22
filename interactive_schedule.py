import sys, csv, cmd, os
from itertools import combinations

# Constant strings used to refer to questions and answers on the survey
EMAIL = "Name"
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
YES = "Yes"
MAYBE = "Maybe"
NO = "No"

# Change these if the wording of survey answers changes (they are case-sensitive)
FULL = "full"
HALF = "half"
# maps all the different ways of saying yes, no, and maybe, because the form writers just HAD to get creative
ANSWER_OPTIONS = {
        "Yes" : YES,
        "I love cooking!" : YES,
        "Less time commitment? Cleaner pika? Sounds great!" : YES,
        "Maybe" : MAYBE,
        "I can do it" : MAYBE,
        "No" : NO,
        "Please no" : NO,
        "Please don't make me" : NO
        }
SHIFT_TIMES = [COOK_MON, CLEAN_MON, COOK_TUE, CLEAN_TUE, COOK_WED, CLEAN_WED, COOK_THU, CLEAN_THU, COOK_FRI, CLEAN_FRI, COOK_SAT, CLEAN_SAT, COOK_SUN, CLEAN_SUN]

# Text in the input CSV that corresponds to each survey question (case-sensitive)
# Note: these are taken from the Google form and need to change if the wording of survey questions changes!
FIELD_HEADERS = { 
        EMAIL : "Email (preferably MIT email if you have one)",
        NEW : "Is this your first time on pika mealplan?",
        FULL_OR_HALF : "Full or half mealplan?",
        COOK : "How enthusiastic are you about cooking?",
        BIGCOOK : "Do you want to big cook?",
        CLEAN : "How enthusiastic are you about cleaning?",
        PAIR : "Anyone you'd like to get paired up with?",
        COOK_MON : "Which nights are you available to cook? [Monday]",
        CLEAN_MON : "Which nights are you available to clean? [Monday]",
        COOK_TUE : "Which nights are you available to cook? [Tuesday]",
        CLEAN_TUE : "Which nights are you available to clean? [Tuesday]",
        COOK_WED : "Which nights are you available to cook? [Wednesday]",
        CLEAN_WED : "Which nights are you available to clean? [Wednesday]",
        COOK_THU : "Which nights are you available to cook? [Thursday]",
        CLEAN_THU : "Which nights are you available to clean? [Thursday]",
        COOK_FRI : "Which nights are you available to cook? [Friday]",
        CLEAN_FRI : "Which nights are you available to clean? [Friday]",
        COOK_SAT : "Which nights are you available to cook? [Saturday]",
        CLEAN_SAT : "Which nights are you available to clean? [Saturday]",
        COOK_SUN : "Which nights are you available to cook? [Sunday]",
        CLEAN_SUN : "Which nights are you available to clean? [Sunday]"
        }
YES_NO_QUESTIONS = [NEW]
YES_MAYBE_NO_QUESTIONS = [COOK, BIGCOOK, CLEAN] + SHIFT_TIMES

# if no answer is provided for these questions, autofill 'no'
AUTOFILL_BLANK_NO = SHIFT_TIMES

SHIFT_TYPES = ["bigcook", "littlecook", "clean"] # N.B. if names are changed here, also change them in Shift.__init__

MON = "Mon"
TUE = "Tue"
WED = "Wed"
THU = "Thu"
FRI = "Fri"
SAT = "Sat"
SUN = "Sun"
DAYS = [MON, TUE, WED, THU, FRI, SAT, SUN]

# codes for weeks
WEEK1 = 1
WEEK2 = 2

# codes for types of "maybe" answers
MAYBE_TYPE = 2
MAYBE_TIME = 3
MAYBE_BIGCOOK = 4

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
            raise Exception("Unrecognized shift type %s" %self.type)

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

def get_notes(data, p, s):
    notes = []
    if data[p][s.time] == MAYBE:
        notes.append(MAYBE_TIME)
    if s.is_cooking:
        if (data[p][COOK] == MAYBE):
            notes.append(MAYBE_TYPE)
        if s.is_big_cooking and (data[p][BIGCOOK] == MAYBE):
            notes.append(MAYBE_BIGCOOK)
    elif not s.is_cooking and data[p][CLEAN] == MAYBE:
        notes.append(MAYBE_TYPE)
    return notes

# returns true if person p strictly prefers cleaning to cooking 
def prefers_cleaning(data, p):
    cook = data[p][COOK]
    clean = data[p][CLEAN]
    if cook == YES: return False
    if cook == NO: return True
    if cook == MAYBE: return (clean == NO)
    
def is_in_week(s, week):
    if isinstance(s, Shift):
        return s.week == week
    return s == "other" + str(week)

# Handle with care. This function has combinatorial complexity due to the
# combinations() calls; the maxn parameter is calibrated to try to avoid
# performance problems.
def detect_clusters(options_by_name, names, slots_per_option, slots_per_name):

    options_by_name = {p : set(options) for p, options in options_by_name.items()}
    names = {p for p in names if slots_per_name[p] > 0}

    # choose the maxn parameter to prevent too much computation
    if len(names) < 15:
        maxn = 7
    elif len(names) < 25:
        maxn = 5
    elif len(names) < 50:
        maxn = 4
    else:
        maxn = 3

    # exclude people who have so many options that they'll never be in a cluster, even one of the maximum size
    max_slots_per_name = max(slots_per_name.values())
    names = {p for p in names if sum(map(lambda x : slots_per_option[x], options_by_name[p])) <= max_slots_per_name*maxn }

    for p in names:
        str_options = list(map(lambda x : "%s (%s)" %(x, slots_per_option[x]), options_by_name[p]))

    clusters = []
    for n in range(2, maxn+1):
        possible_clusters = {frozenset(comb) : set() for comb in combinations(names, n)}
        for members, S in possible_clusters.items():
            for p in members:
                S.update(options_by_name[p])
        to_remove = set()
        for members, S in possible_clusters.items():
            nslots_members = sum(map(lambda p : slots_per_name[p], members))
            nslots_options = sum(map(lambda x : slots_per_option[x], S))
            if 0 < nslots_options and nslots_options <= nslots_members: 
                clusters.append((members, S))
                to_remove.update(members)
        names = names - to_remove

    # if multiple clusters actually correspond to the same shifts, just group them together
    by_shift = {frozenset(S) : set() for members, S in clusters}
    for members, S in clusters:
        by_shift[frozenset(S)].update(members)
    clusters = [(members, S) for S, members in by_shift.items()]

    return clusters

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

        # IMPORTANT: if update() is not called after every state change, then cache will cause stale results
        self.cache = None

    def is_person(self, p):
        return p in self.people
    
    def is_str(self, s):
        return (s in self.other_assignments) or (s in map(str, self.shifts))

    def has_shift(self, p, shiftname):
        if not self.is_person(p):
            return False
        return any(map(lambda s: str(s) == shiftname, self.get_current_shifts(p)))
    
    def has_shift_for_week(self, p, week):
        for s in self.get_current_shifts(p):
            if isinstance(s, Shift) and s.week == week:
                return True
            elif s == "other" + str(week):
                return True
        return False
    
    def get_current_shifts(self, p):
        shifts = [s for s, p2 in self.assignments.items() if p == p2]
        return shifts + [s for s, people in self.other_assignments.items() if p in people]
    
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
        people = [person]
        if person is None:
            remaining_shifts = self.get_remaining_shifts()
            people = [p for p in self.people if remaining_shifts[p] > 0]
        notes = []
        for p in people:
            for s in Schedule.shifts:
                codes = get_notes(self.data, p, s)
                notes.extend(map(lambda c : make_note(p, s, c), codes))
            if self.data[p][NEW]:
                notes.append("%s is new to mealplan" %p)
            pair_requests = self.data[p][PAIR]
            if len(pair_requests) != 0:
                notes.append("%s asked to work with %s" %(p, ", ".join(pair_requests)))
        return list(set(notes))

    def get_answer(self, name, shift, maybe_is_no=False):
        relevant_responses = [self.data[name][shift.time]]
        if shift.is_cooking:
            relevant_responses.append(self.data[name][COOK])
            if shift.is_big_cooking:
                relevant_responses.append(self.data[name][BIGCOOK])
        else: 
            relevant_responses.append(self.data[name][CLEAN])
        if NO in relevant_responses:
            return NO
        if MAYBE in relevant_responses:
            if maybe_is_no:
                return NO
            else:
                return MAYBE
        return YES

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
            if person in self.other_assignments[shift]:
                print("%s is already assigned to %s" %(person, shift))
                return
            self.other_assignments[shift].append(person)
            self.update()
            self.auto_assign()
            return
        else:
            for s in self.get_unassigned_shifts():
                if str(s) == shift:
                    self.assignments[s] = person
                    self.update()
                    self.auto_assign()
                    return
        # should never get here 
        print("Could not assign shift; all shifts of type %s are taken. Did you type the correct week?" %shift)

    def unassign(self, person, shiftname):
        if shiftname == "other1" or shiftname == "other2":
            self.other_assignments[shiftname].remove(person)
        else:
            to_unassign = list(filter(lambda s: str(s) == shiftname, self.get_current_shifts(person)))
            if len(to_unassign) == 0:
                print("%s is not assigned to shift %s" %(person, shift))
            for shift in to_unassign:
                del self.assignments[shift]
        self.update()
        self.auto_assign()
        
    def remove_rule(self, r):
        if r not in self.rule_commands:
            print("Unrecognized rule name %s. Recognized rule names are: %s" %(r, ", ".join(self.rule_commands.keys())))
        if r in self.shift_person_rules:
            del self.shift_person_rules[r]
        else:
            del self.person_person_rules[r]
        del self.rule_commands[r]
        self.update()
        self.auto_assign()

    def next_rule_name(self):
        return "rule" + str(self.rule_counter)

    def add_person_person_rule(self, p1, p2):
        if p1 == p2 and p1 != "new":
            print("You cannot exclude someone from cooking with themselves. What's your problem?")
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
        self.update()
        self.auto_assign()

    def add_shift_person_rule(self, p1, x):
        cond1 = lambda p : p == p1
        cond2 = lambda s : str(s) == x
        if p1 == "new":
            cond1 = lambda p : self.data[p][NEW]
        if x in SHIFT_TYPES:
            cond2 = lambda s : s.type == x
        rule_name = self.next_rule_name()
        self.shift_person_rules[rule_name] = lambda p, s : not (cond1(p) and cond2(s))
        self.rule_counter += 1
        self.rule_commands[rule_name] = "exclude %s %s" %(p1, x)
        self.update()
        self.auto_assign()

    def get_remaining_shifts(self):
        remaining_shifts = {p : (1 if self.data[p][FULL_OR_HALF] == HALF else 2) for p in self.people}
        for p in self.assignments.values():
            remaining_shifts[p] -= 1
        for week in self.other_assignments:
            for p in self.other_assignments[week]:
                remaining_shifts[p] -= 1
        return remaining_shifts

    # mapping from each person to all shifts that they could work
    def get_shifts_by_people(self, maybe_is_no):
        possibilities_by_shift = self.get_possibilities_by_shift(maybe_is_no=maybe_is_no)
        shifts_by_people = {p : [] for p in self.people}
        for s in self.shifts:
            for p, _ in possibilities_by_shift[s]:
                shifts_by_people[p].append(s)
        return shifts_by_people
        
    def get_warnings(self):
        if self.cache != None:
            return self.cache["warnings"]
        possibilities_by_shift = self.get_possibilities_by_shift()
        possibilities_by_person = self.get_shifts_by_people(False)
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
                shifts = list(filter(lambda s : is_in_week(s, week), self.get_current_shifts(p)))
                if len(shifts) > 1:
                    warnings.append("%s has multiple shifts in the same week (week %s)" %(p, week))
            possible = possibilities_by_person[p]
            if len(possible) < remaining_shifts[p]:
                warnings.append("%s needs %s more shifts but is only available for %s (%s)" %(p, remaining_shifts[p], len(possible), " and ".join(map(str, possible))))
        for s, possibilities in possibilities_by_shift.items():
            if len(possibilities) == 0:
                warnings.append("No one is available for shift %s" %s)

        shifts_per_shift_time = {s.time: 0 for s in Schedule.shifts}
        for s in Schedule.shifts:
            if s not in self.assignments:
                shifts_per_shift_time[s.time] += 1
        clusters = detect_clusters({p : list(map(lambda s : s.time, options)) for p, options in possibilities_by_person.items()}, self.people, shifts_per_shift_time, remaining_shifts)
        for people, shift_times in clusters:
            shifts_possible = []
            for t in shift_times:
                shifts_possible.extend([s for s in Schedule.shifts if s.time == t and s not in self.assignments])
            shifts_needed = sum(map(lambda p : remaining_shifts[p], people))
            nshifts = len(set(shifts_possible))
            shifts_possible = list(set(map(str, shifts_possible))) # unique names
            warnings.append("%s, between them, need %s shifts but can only do %s shifts: %s. Assigning others to those shifts will make the schedule unsatisfiable, so it's highly recommended to assign these people first." %(", ".join(list(map(self.format_name, people))), shifts_needed, nshifts, ", ".join(shifts_possible)))
        
        warnings.sort()
        return list(set(warnings))

    def get_possible_pairings(self, maybe_is_no):
        # person x person x list shift
        shifts_by_people = self.get_shifts_by_people(maybe_is_no)
        available_people = [p for p, n in self.get_remaining_shifts().items() if n > 0]
        out = {}
        for p1 in self.people:
            for p2 in self.data[p1][PAIR]:
                if p2 not in available_people:
                    continue
                if (p2, p1) in out:
                    continue # we've already done this suggestion
                out[(p1, p2)] = [(s1, s2) for s1 in shifts_by_people[p1] for s2 in self.paired_shifts[s1] if s2 in shifts_by_people[p2]]
        return [(p1, p2, options) for (p1, p2), options in out.items() if len(options) > 0]

    def suggest_new_cook(self, maybe_is_no):
        shifts_by_people = self.get_shifts_by_people(maybe_is_no)
        new_people = [p for p, n in self.get_remaining_shifts().items() if n > 0 and self.data[p][NEW] and not prefers_cleaning(self.data, p)]
        out = []
        for p in new_people:
            available_cooking_shifts = list(filter(lambda s : s.is_cooking and not s.is_big_cooking, shifts_by_people[p]))
            available_cleaning_shifts = list(filter(lambda s : not s.is_cooking, shifts_by_people[p]))
            if len(available_cooking_shifts) != 0:
                out.append((p, available_cooking_shifts, "new people should cook if possible"))
        return out

    def suggest_last_yes(self, maybe_is_no):
        possibilities_by_shift = self.get_possibilities_by_shift(maybe_is_no=maybe_is_no)
        shifts_by_person = {p : [] for p in self.people}
        for s in self.get_unassigned_shifts():
            yes_people = list(filter(lambda x : len(x[1]) == 0, possibilities_by_shift[s]))
            if len(yes_people) == 1:
                shifts_by_person[yes_people[0][0]].append(s)
        out = []
        for p, shift_options in shifts_by_person.items():
            if len(shift_options) > 0:
                out.append((p, shift_options, "they are the only person with no hesitations about these shift times/types")) 
        return out
    
    def suggest_constrained_people(self, maybe_is_no):
        remaining_shifts = self.get_remaining_shifts()
        possibilities_by_person = self.get_shifts_by_people(maybe_is_no)
        out = []
        for p in self.people:
            possible = possibilities_by_person[p]
            if len(possible) <= remaining_shifts[p]*2 and len(possible) != 0 and remaining_shifts[p] > 0:
                out.append((p, possible, "they need %s more shifts and are only available for %s" %(remaining_shifts[p], len(possible)))) 
        return out

    def pairing_requestors(self, p1, p2):
        out = []
        if p2 in self.data[p1][PAIR]:
            out.append(p1)
        if p1 in self.data[p2][PAIR]:
            out.append(p2)
        return out
    
    def make_pairing_justification(self, p1, p2):
        requestors = self.pairing_requestors(p1, p2)
        justification = "if you see this then your pairing wasn't requested by either party, that's confusing"
        if len(requestors) == 2:
            justification = "so %s and %s can work together (mutually requested)" %(p1, p2)
        elif requestors == [p1]:
            justification = "so %s and %s can work together as requested by %s" %(p1, p2, p1)
        elif requestors == [p2]:
            justification = "so %s and %s can work together as requested by %s" %(p1, p2, p1)
        return justification

    # list (shift x shift) -> string
    def format_pairing_options(self, shift_options):
        cook_days = list(set([s1.day for s1, s2 in shift_options if s1.is_cooking]))
        clean_days = list(set([s1.day for s1, s2 in shift_options if not s1.is_cooking]))
        cook_days.sort(key=lambda d : DAYS.index(d))
        clean_days.sort(key=lambda d : DAYS.index(d))
        cook_str = "/".join(cook_days)
        clean_str = "/".join(clean_days)
        if len(cook_days) == 0:
            option_str = "clean on %s" %clean_str 
        elif len(clean_days) == 0:
            option_str = "cook on %s" %cook_str
        else:
            option_str = "cook on %s OR clean on %s" %(cook_str, clean_str)
        return option_str
    
    # list shift -> string
    def format_shift_options(self, shift_options):
        options_by_type = {}
        for t in SHIFT_TYPES:
            options = list(set(map(lambda s : s.day, filter(lambda s : s.type == t, shift_options))))
            options.sort(key=lambda d : DAYS.index(d))
            options_by_type[t] = "/".join(options) 
        return " OR ".join(["to %s on %s" %(t, options) for t, options in options_by_type.items() if len(options) > 0])

    def format_name(self, name):
        if self.data[name][FULL_OR_HALF] == HALF:
            return name + "*"
        return name
        
    def get_suggestions(self, maybe_is_no=False):
        if self.cache != None and not maybe_is_no:
            return self.cache["suggestions"]

        # collect non-pairing suggestions in the form person x list shift x justification -- e.g. ("joe", [cookmon1, cookmon2, ... ], "new people should cook")
        suggestions = []
        suggestions.extend(self.suggest_new_cook(maybe_is_no))
        suggestions.extend(self.suggest_last_yes(maybe_is_no))

        # these are generally things that kind of have to be done, so they always get displayed first
        constrained_people = self.suggest_constrained_people(False) # maybe_is_no always set to false for this one

        # collect pairing suggestions -- these are treated slightly differently than other kinds
        # each pairing has the type person x person x list (shift x shift) -- e.g. ("joe", "zelda", [(bigcookmon1, cookmon1), (cleantue1, cleantue1)])
        all_pairings = self.get_possible_pairings(maybe_is_no)
        
        # if someone requests to pair with a ton of people, it can clutter the results without adding much information
        # therefore, don't make suggestions based on a person's pairing requests until <= 5 of their requests are possible
        request_count = {p : 0 for p in self.people}
        for p1, p2, shift_options in all_pairings:
            req = self.pairing_requestors(p1, p2)
            if len(req) == 1:
                request_count[req[0]] += 1
        pairings = []
        for p1, p2, shift_options in all_pairings:
            req = self.pairing_requestors(p1, p2)
            if len(req) == 1 and request_count[req[0]] > 5:
                continue
            else:
                pairings.append((p1, p2, shift_options))

        # if a suggestion has been repeated across different categories, put it in a special map with type (person x shift) -> list justification
        # first, we figure out how many times an assignment has been suggested, then aggregate the justifications
        suggestion_count = {}
        for person, shift_options, just in suggestions:
            for shift in shift_options:
                if (person, shift) not in suggestion_count:
                    suggestion_count[(person, shift)] = 0
                suggestion_count[(person, shift)] += 1
        # aggregate justifications
        repeated_suggestions = {assignment : [] for assignment, count in suggestion_count.items() if count > 1} 
        for person, shift_options, justification in suggestions:
            for shift in shift_options:
                assignment = (person, shift)
                if assignment in repeated_suggestions:
                    repeated_suggestions[assignment].append(justification)

        # first, sort in order of number of options, so we see most-constrained first
        pairings.sort(key=lambda t: len(t[2]))
        suggestions.sort(key=lambda t:len(t[1]))
        
        # now, sort in order of most-justified:
        # 1) repeated suggestions with > 2 justifications
        # 2) mutually-requested pairings
        # 3) repeated suggestions with 2 justifications
        # 4) singly-requested pairings
        # 5) other suggestions
        out = []
        for person, shift_options, justification in constrained_people:
            out.append("assign %s %s because %s" %(self.format_name(person), self.format_shift_options(shift_options), justification))
        for (person, shift), justifications in filter(lambda kv: len(kv[1]) > 2, repeated_suggestions.items()):
            out.append("assign %s %s %s" %(self.format_name(person), shift, " and ".join(justifications)))
        for p1, p2, shift_options in  pairings:
            if len(self.pairing_requestors(p1, p2)) == 2:
                out.append("pair %s and %s (mutually requested) by assigning them to %s" %(self.format_name(p1), self.format_name(p2), self.format_pairing_options(shift_options))) 
        for (person, shift), justifications in filter(lambda kv: len(kv[1]) == 2, repeated_suggestions.items()):
            out.append("assign %s %s %s" %(self.format_name(person), shift, " and ".join(justifications)))
        for p1, p2, shift_options in  pairings:
            req = self.pairing_requestors(p1, p2)
            if len(req) == 1:
                out.append("pair %s and %s (requested by %s) by assigning them to %s" %(self.format_name(p1), self.format_name(p2), req[0], self.format_pairing_options(shift_options))) 
        for person, shift_options, justification in suggestions:
            if len(shift_options) == 1 and (person, shift_options[0]) in repeated_suggestions:
                continue # we don't need to repeat something eclipsed by a repeated suggestion
            out.append("assign %s %s because %s" %(self.format_name(person), self.format_shift_options(shift_options), justification))
        return out 

    def get_possibilities_by_shift(self, maybe_is_no=False):
        if self.cache != None and not maybe_is_no:
            return self.cache["pbs"]
        possibilities_by_shift = { s : [] for s in Schedule.shifts}
        for s in self.assignments:
            possibilities_by_shift[s] = [(self.assignments[s], [])]
        available_people = [p for p, n in self.get_remaining_shifts().items() if n > 0]
        for s in self.get_unassigned_shifts():
            for p in available_people:
                if self.get_answer(p, s, maybe_is_no) != NO and not self.has_shift_for_week(p, s.week) and not self.rules_broken(p, s):
                    possibilities_by_shift[s].append((p, get_notes(self.data, p, s)))
        return possibilities_by_shift

    # refresh the cache
    def update(self):
        self.cache = None # needed to trigger recalculations
        self.cache = {
                "pbs" : self.get_possibilities_by_shift(),
                "suggestions" : self.get_suggestions(),
                "warnings" : self.get_warnings()
                }

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
            self.update()
            new_assignment = self.auto_assign_one() 

    def get_state_summary(self):
        return (set(self.assignments), set(self.rule_commands.values()))


class Loop(cmd.Cmd):
    prompt = "Enter your move (type '?' or 'help' for options): "
    file=None
    maybe_is_no = False
    # number of arguments expected by each command
    nargs = {
            "autoassign": [1],
            "exit" : [0],
            "save" : [1],
            "show" : [1, 2],
            "assign" : [2],
            "unassign": [2],
            "exclude" : [2],
            "remove" : [2] }

    def __init__(self, data):
        super().__init__()
        self.state = Schedule(data)
        self.prev_state_summary = self.state.get_state_summary()
    
    def tips():
        lines = []
        lines.append(" - Parentheses around a name indicate they only 'maybe' want that shift time/type; type 'show notes <person's name>' for details")
        lines.append(" - The 'other' category is for exempt house officers or miscellaneous shifts, like tiny cook, fridge ninja, or brunch cook")
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
        lines.append("\tshow status\t\t- display the current state of assignments/possibilities")
        lines.append("\tshow status <shift_type>\t- display the current state of assignments/possibilities for shifts of this type (%s, %s, or %s)" %tuple(SHIFT_TYPES))
        lines.append("\tshow rules\t\t- display the rules currently in effect")
        lines.append("\tshow assignments\t- display the shift assignments currently in effect")
        lines.append("\tshow suggestions\t- suggest next moves")
        lines.append("\tshow notes\t\t- display additional information (e.g. 'maybe' answers) about all people who are still need to be assigned to a shift")
        lines.append("\tshow notes <person>\t- display additional information (e.g. 'maybe' answers) about <person>")
        lines.append("\tshow options <person>\t- display all shifts that <person> could be assigned to")
        lines.append("")
        lines.append("\tassign <person> <shift>\t\t- assign <person> to <shift> (e.g. 'assign joe %s')" %Schedule.shifts[0])
        lines.append("\tassign <person> other\t\t- assign <person> to some shift that doesn't appear here (e.g. fridge ninja or tiny cook), so that they don't show up as possibilities for other shifts")
        lines.append("\tunassign <person> <shift>\t- unassign <person> from <shift>")
        lines.append("\tunassign <person> other\t\t- unassign <person> from the 'other' category")
        lines.append("\tautoassign off\t\t- turn off autoassign (on by default), which is when the system automatically identifies and fills shifts that can only be filled one way")
        lines.append("\tautoassign on\t\t- turn autoassign back on")
        lines.append("")
        lines.append("\texclude <person> <shift_type>\t- exclude <person> from certain shift types ('%s',' %s', or '%s')" %tuple(SHIFT_TYPES))
        lines.append("\texclude new <shift_type>\t- exclude all people new to mealplan from certain shift types ('%s', '%s', or '%s')" %tuple(SHIFT_TYPES))
        lines.append("\texclude <person> <shift>\t- exclude <person> from a certain shift (e.g. '%s' or '%s')" %(str(Schedule.shifts[0]), str(Schedule.shifts[3])))
        lines.append("\texclude new <shift>\t\t- exclude all people new to mealplan from a certain shift (e.g. '%s' or '%s')" %(str(Schedule.shifts[0]), str(Schedule.shifts[3])))
        lines.append("\texclude <person> <person>\t- exclude two people from working together") 
        lines.append("\texclude new <person>\t- exclude someone from working with new people") 
        lines.append("\texclude new new\t\t- exclude possibilities where two people who are *both* new to mealplan would work together") 
        lines.append("\tremove rule <rule name>\t- remove a rule created by 'exclude', based on the name shown by 'show rules'")
        lines.append("")
        lines.append("\tsave <file>\t\t- save current assignments and rules to a new file with the name <file> (fails if <file> exists)")
        lines.append("\texit\t\t- close program")
        return "\n".join(lines)

    def complete_load(self, text, line, begidx, endidx):
        cmd_size = len("load ") # index of end of command
        if begidx == cmd_size:
            dirname, filename = os.path.split(text)
            if dirname == '':
                # current directory
                return [f for f in os.listdir() if f.startswith(filename)]
            else:
                return ["%s/%s" %(dirname, f) for f in os.listdir(dirname) if f.startswith(filename)]
        else:
            return [] # unexpected begin index; no completions

    def complete_show(self, text, line, begidx, endidx):
        cmd_size = len("show ") # index of end of command
        if begidx == cmd_size:
            # we're completing the first word
            return [x for x in ["status", "rules", "assignments", "suggestions", "notes", "options"] if x.startswith(text)]
        elif begidx > cmd_size:
            # we're completing the second word; look at what the first word is
            args = line.split(" ")
            if args[1] == "notes" or args[1] == "options":
                return [p for p in self.state.people if p.startswith(text)]
            elif args[1] == "status":
                return [t for t in SHIFT_TYPES if t.startswith(text)]
        else:
            return [] # unexpected begin index; no completions
    
    def complete_unassign(self, text, line, begidx, endidx):
        cmd_size = len("unassign ") # index of end of command
        if begidx == cmd_size:
            # we're completing the first word -- suggest people
            return [p for p in self.state.people if p.startswith(text)]
        elif begidx > cmd_size:
            # we're completing the second word; suggest shifts the person is assigned to
            p = line.split(" ")[1]
            others = [x for x in ["other1", "other2"] if x.startswith(text) and self.state.has_shift(p, x)]
            return [str(s) for s in Schedule.shifts if self.state.has_shift(p, str(s)) and str(s).startswith(text)] + others
        else:
            return [] # unexpected begin index; no completions
    
    def complete_assign(self, text, line, begidx, endidx):
        cmd_size = len("assign ") # index of end of command
        if begidx == cmd_size:
            # we're completing the first word -- suggest people
            return [p for p in self.state.people if p.startswith(text)]
        elif begidx > cmd_size:
            # we're completing the second word; suggest shifts that are currently unassigned
            p = line.split(" ")[1]
            others = [x for x in ["other1", "other2"] if x.startswith(text)]
            return [str(s) for s in Schedule.shifts if str(s).startswith(text) and s not in self.state.assignments] + others
        else:
            return [] # unexpected begin index; no completions

    def complete_exclude(self, text, line, begidx, endidx):
        cmd_size = len("exclude ") # index of end of command
        if begidx == cmd_size:
            # first argument can be person or 'new'
            options = self.state.people + ["new"]
            return [x for x in options if x.startswith(text)]
        elif begidx > cmd_size:
            # second argument options depend on first argument 
            args = line.split(" ")
            options = self.state.people + list(map(str, Schedule.shifts)) + SHIFT_TYPES
            if args[1] == "new":
                options.append("new")
            return [x for x in options if x.startswith(text)]
        else:
            return [] # unexpected begin index; no completions

    def preloop(self):
        self.state.update()
        self.state.auto_assign()

    def postcmd(self, stop, line):
        if self.state.is_complete():
            self.display_complete()
        # display warnings if the state changed
        summary = self.state.get_state_summary()
        if summary != self.prev_state_summary:
            self.display_warnings()
            self.prev_state_summary = self.state.get_state_summary()

        return stop

    def emptyline(self):
        pass # do nothing on empty input; overrides default Cmd behavior

    def get_args(self, cmd, arg_string):
        args = [a.strip().lower() for a in arg_string.split(" ") if a.strip() != ""]
        if cmd in self.nargs and len(args) not in self.nargs[cmd]:
            print("Unexpected number of arguments to '%s'! Expected %s, got %s : %s" %(cmd, " or ".join(list(map(str, self.nargs[cmd]))), len(args), ", ".join(args)))
            return None
        return args

    def check_person_arg(self, x, new_ok=False):
        if (new_ok and x == "new") or self.state.is_person(x):
            return True
        print ("Unrecognized person %s. Recognized people are : %s" %(x, ", ".join(self.state.people)))
        return False
 
    def check_shift_arg(self, x):
        shift_names = [str(s) for s in Schedule.shifts]
        if self.state.is_str(x):
            return True
        else:
            print("Unrecognized shift %s. Recognized shifts are : %s" %(x, ", ".join(list(set(shift_names)))))
            return False

    # returns True if successful
    def save(self, filename):
        try:
            f = open(filename, "x")
            for shiftname, people in self.state.other_assignments.items():
                for person in people:
                    f.write("assign %s %s\n" %(person, shiftname))
            for shift, person in self.state.assignments.items():
                f.write("assign %s %s\n" %(person, str(shift)))
            for cmd in self.state.rule_commands.values():
                f.write("%s\n" %cmd)
            f.close()
            return True
        except (IOError, FileExistsError): # IOError is raised on python versions before 3.3, in case people don't update their shit
            return False

    def autosave(self):
        if len(self.state.assignments) == 0 and len(self.state.other_assignments) == 0 and len(self.state.rule_commands) == 0:
            return
        i = 0
        success = False
        while not success:
            name = "autosave%s.txt" %i 
            success = self.save(name)
            if success:
                print("Saved assignments and rules to  %s; restore using the 'load' command." %name)
            i += 1

    def do_exit(self, arg):
        print("Goodbye!")
        self.autosave()
        return True

    def do_load(self, arg):
        args = self.get_args("load", arg)
        if args == None:
            self.default("load " + arg)
            return
        try:
            f = open(args[0], "r")
            for line in f:
                self.onecmd(line.strip("\n"))
            f.close()
            print("Successfully loaded %s." %args[0])
            self.display_warnings()
        except IOError as e:
            print("Could not load file '%s'. Does the file exist?" %args[0])

    def do_save(self, arg):
        # save assignments and rules to a file
        args = self.get_args("save", arg)
        if args == None:
            self.default("save " + arg)
        if self.save(args[0]):
            print("Successfully saved. Use the command 'load %s' in any session to restore all current assignments and rules." %args[0])
        else:
            print("Could not open '%s'. Does a file with that name already exist?" %args[0])
    
    def do_autoassign(self, arg):
        args = self.get_args("autoassign", arg) 
        if args == None:
            self.default("autoassign " + arg)
            return
        if args[0] == "on":
            self.state.set_autoassign(True)
        elif args[0] == "off":
            self.state.set_autoassign(False)
        else:
            self.default("autoassign" + args)
    
    def do_assign(self, arg):
        args = self.get_args("assign", arg)
        if args == None:
            self.default("assign " + arg)
            return
        person, shift = args
        if not self.check_person_arg(person): return
        # check for case in which we assign someone to e.g. 'bigcookmon' and they get assigned to both weeks at once; treat as though it's two commands
        if self.state.is_str(shift + "1"):
            self.do_assign("%s %s" %(person, shift + "1"))
            self.do_assign("%s %s" %(person, shift + "2"))
            return
        if not self.check_shift_arg(shift): return
        print("Assigning %s to shift %s" %(person, shift))
        self.state.assign(person, shift)

    def do_unassign(self, arg):
        args = self.get_args("unassign", arg)
        if args == None:
            self.default("unassign " + arg)
            return
        person, shift = args
        if not self.check_person_arg(person): return
        if self.state.is_str(shift + "1"):
            self.do_unassign("%s %s" %(person, shift + "1"))
            self.do_unassign("%s %s" %(person, shift + "2"))
            return
        if not self.check_shift_arg(shift): return
        if not self.state.has_shift(person, shift):
            print("%s is not currently assigned to shift %s. Did you type the right week?" %(person, shift))
            return
        print("Unassigning %s from shift %s" %(person, shift))
        self.state.unassign(person, shift)
    
    def do_remove(self, arg):
        args = self.get_args("remove", arg)
        if args == None or not args[0] == "rule":
            self.default("remove " + arg)
            return
        r = args[1]
        print("Removing rule %s (%s)" %(r, self.state.rule_commands[r]))
        self.state.remove_rule(r)
 
    def do_exclude(self, arg):
        args = self.get_args("exclude", arg)
        if args == None:
            self.default("exclude " + arg)
            return
        p1, x = args
        if not self.check_person_arg(p1, new_ok=True): return
        print("Adding rule %s (%s). Type 'show rules' to view all rules." %(self.state.next_rule_name(), " ".join(["exclude", p1, x])))
        if self.state.is_str(x) or x in SHIFT_TYPES: 
            self.state.add_shift_person_rule(p1, x)
        elif x == "other":
            print("'other' shifts cannot be used in 'exclude', and there's no reason to do it anyway, so stoppit")
            return
        else:
            if not self.check_person_arg(x, new_ok=True): return
            self.state.add_person_person_rule(p1, x)

    def do_show(self, arg):
        args = self.get_args("show", arg)
        if args == None:
            self.default("show " + arg)
            return
        line = "show " + args[0]
        if len(args) == 1:
            cmd2 = args[0]
            if cmd2 == "status":
                self.display_status()
            elif cmd2 == "rules":
                self.display_rules()
            elif cmd2 == "assignments":
                self.display_assignments()
            elif cmd2 == "suggestions":
                self.display_suggestions(True)
            elif cmd2 == "notes":
                self.display_notes()
            else:
                self.default(line)
        elif len(args) == 2 and args[0] == "notes":
            person = args[1]
            if not self.check_person_arg(person): return
            self.display_notes(person)
        elif len(args) == 2 and args[0] == "options":
            person = args[1]
            if not self.check_person_arg(person): return
            self.display_options(person)
        elif len(args) == 2 and args[0] == "status":
            t = args[1]
            if not t in SHIFT_TYPES: return
            self.display_status(shift_type=t)
        elif len(args) == 2 and args[0] == "suggestions":
            if args[1] != "all":
                self.default(line)
            self.display_suggestions(False)
        else:
            line = "show " + arg
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

    def display_options_from_shifts(self, person, shifts):
        # helper for display_options; prints the options for a given person out of a provided list of shifts 
        shifts.sort(key=lambda s: (s.week * 2 * len(DAYS) + DAYS.index(s.day) * 2 + (0 if s.is_cooking else 1)))
        option_strings = []
        for s in shifts:
            if self.state.get_answer(person, s, False) == NO:
                continue
            n = len(get_notes(self.state.data, person, s))
            option_strings.append("(" * n + str(s) + ")" * n)
        options_nodup = [] # could use set(), but would mess up order
        for s in option_strings:
            if s not in options_nodup:
                options_nodup.append(s)
        print(", ".join(options_nodup))

    def display_options(self, person):
        print("\nShifts that are currently UNASSIGNED: ")
        self.display_options_from_shifts(person, self.state.get_unassigned_shifts())
        print("\nShifts that are currently ASSIGNED: ")
        self.display_options_from_shifts(person, list(self.state.assignments.keys()))
        print("")

    def display_complete(self):
        print("ALL SHIFTS ASSIGNED!")
        remaining_shifts = self.state.get_remaining_shifts()
        nonzero_remaining_shifts = {p : rem for p, rem in remaining_shifts.items() if rem != 0}
        if len(nonzero_remaining_shifts) != 0:
            print("Some people have remaining shifts (they can be assigned as tiny cooks etc):")
            for p, rem in remaining_shifts.items():
                if rem != 0:
                    print("%s : %s shifts remaining" %(p, rem))

    def display_suggestions(self, strict):
        suggestions = self.state.get_suggestions(maybe_is_no=strict)
        if len(suggestions) == 0:
            print("\t No suggestions, sorry!")
            if strict:
                print("Try 'show suggestions all' to show suggestions that do not avoid 'maybe' answers.")
            return
        print("Suggested moves (%s):" %len(suggestions))
        for s in suggestions:
            print("\t- %s" %s)
        if strict:
            print("The above suggestions don't include options that would give someone a shift they only 'maybe' want. Use 'show suggestions all' to remove this constraint.")

    def display_rules(self):
        for r in (sorted(self.state.rule_commands.keys())):
            print("%s : %s" %(r, self.state.rule_commands[r]))
        if len(self.state.rule_commands) == 0:
            print("No rules yet!")

    def display_assignments(self):
        for s in self.state.assignments:
            print("%s : %s" %(s, self.state.assignments[s]))
        other_assigned = False
        for w in [WEEK1, WEEK2]:
            assigned_to_other = self.state.get_other(w)
            if len(assigned_to_other) > 0:
                print("other%s : %s" %(w, ", ".join(assigned_to_other)))
                other_assigned = True
        if len(self.state.assignments) == 0 and not other_assigned:
            print("No assignments yet!")

    def display_warnings(self):
        print("")
        for warning in self.state.get_warnings():
            print("WARNING: %s" %warning)
    
    def display_status_list(self, shift_type=None):
        table = {str(s) : [] for s in Schedule.shifts}
        possibilities_by_shift = self.state.get_possibilities_by_shift(maybe_is_no=self.maybe_is_no)
        for s in Schedule.shifts:
            if s in self.state.assignments:
                table[str(s)].append((0, "[%s]" %self.state.assignments[s]))
            else:
                for p, notes in possibilities_by_shift[s]:
                    p = self.state.format_name(p)
                    n = len(notes)
                    table[str(s)].append((n, ("(" * n) + p + (")" * n)))
        for c in table:
            table[c] = sorted(list(set(table[c]))) # remove duplicate entries for cleaning shifts
            table[c] = list(map(lambda x : x[1], table[c]))

        week, day = None, None
        already_printed = []
        for s in Schedule.shifts:
            if shift_type is not None and s.type != shift_type:
                continue
            if s.week != week:
                print("\nWeek %s\n======" %s.week)
                print("other%s: %s\n" %(s.week, ", ".join(self.state.get_other(s.week))))
            elif s.day != day:
                print("")
            week, day = s.week, s.day
            if str(s) not in already_printed:
                maybe_count = len(list(filter(lambda x:x.startswith("("), table[str(s)])))
                assigned_count = len(list(filter(lambda x:x.startswith("["), table[str(s)])))
                yes_count = len(table[str(s)]) - assigned_count - maybe_count
                if yes_count == 0 and maybe_count == 0:
                    count_str = '' # this shift is fully assigned; don't show the count
                else:
                    count_str = "(%s yes, %s maybe) " %(yes_count, maybe_count)
                print("%s %s: %s" %(s, count_str, "; ".join(table[str(s)]))) 
                already_printed.append(str(s))
        self.display_warnings()

    def display_status(self, shift_type=None):
        table = {str(s) : [] for s in Schedule.shifts}
        possibilities_by_shift = self.state.get_possibilities_by_shift(maybe_is_no=self.maybe_is_no)
        for s in Schedule.shifts:
            if s in self.state.assignments:
                table[str(s)].append((0, "[%s]" %self.state.assignments[s]))
            else:
                for p, notes in possibilities_by_shift[s]:
                    p = self.state.format_name(p)
                    n = len(notes)
                    table[str(s)].append((n, ("(" * n) + p + (")" * n)))
        for c in table:
            table[c] = sorted(list(set(table[c]))) # remove duplicate entries for cleaning shifts
            table[c] = list(map(lambda x : x[1], table[c]))

        cols, _ = os.get_terminal_size()
        first_col_size = max(map(len, SHIFT_TYPES)) + 3 # +3 is for a divider and a space on each side of it 
        cols_per_day = int((cols - first_col_size - 3) / (len(DAYS))) - 3 # subtract 3 to leave room for a divider pipe and a space on either side # TODO: use this to determine whether to do the grid or not

        WEEKS = [WEEK1, WEEK2] # TODO: make this a constant
        shift_types = [shift_type] if shift_type != None else SHIFT_TYPES
        table2 = {d : {t : {w : "" for w in WEEKS} for t in shift_types} for d in DAYS}
        for s in Schedule.shifts:
            if s.type in shift_types:
                table2[s.day][s.type][s.week] = table[str(s)]

        display_rows = []
        display_rows.append([""] + [d for d in DAYS]) # first row is the header 
        for t in shift_types:
            row = [t] # first column is the type of shift
            for d in DAYS:
                n_subrows = len(set(map(frozenset, table2[d][t].values())))
                if n_subrows == 1:
                    subrows = [table2[d][t][WEEK1]]
                else:
                    subrows = [table2[d][t][w] for w in WEEKS]
                # okay, now each subrow is actually a list of names
                subrow_strings = []
                for subrow in subrows:
                    subrow_lines = []
                    line = ""
                    for name in subrow:
                        # TODO: things mess up if a name is longer than the number of columns
                        # if we can add it to the most recent line, do so
                        new_line = line + name + "; "
                        if len(new_line) <= cols_per_day:
                            line = new_line
                        else: # start a new line
                            subrow_lines.append(line)
                            line = name + "; "
                            while len(line) > cols_per_day:
                                subrow_lines.append(line[:cols_per_day])
                                line = line[cols_per_day:]
                    subrow_lines.append(line) # add last line
                    subrow_lines = ['{0:{width}s}'.format(line, width=cols_per_day) for line in subrow_lines]
                    subrow_strings.append("".join(subrow_lines))
                divider = "-" * cols_per_day
                row.append(divider.join(subrow_strings))
            display_rows.append(row)


        row_max_chars = [max(r, key=len) for r in display_rows]
        row_heights = [int(len(c) / cols_per_day) + 1 for c in row_max_chars]

        display_lines = []
        row_divider = " +" + ("-" * ((cols_per_day + 3) * len(DAYS) + first_col_size + 2)) + "+ "
        display_lines.append(row_divider)
        for i in range(len(display_rows)):
            for j in range(row_heights[i]):
                # to form each line, take the characters in range(cols_per_day*j, cols_per_day*(j+1)) from each cell
                line = []
                for k in range(len(display_rows[i])):
                    cell = display_rows[i][k]
                    width = first_col_size if k == 0 else cols_per_day
                    line.append("{0:{width}s}".format(cell[width * j:width * (j+1)], width=width))
                display_lines.append(" | " + " | ".join(line) + " | ")
            display_lines.append(row_divider)

        for x in display_lines:
            print(x)

        self.display_warnings()

def parse_name(email):
    return email.lower().split("@mit")[0].replace(" ", "")

def reformat_multiple_choice(data_rows):
    yes_no_options = [k for k, v in ANSWER_OPTIONS.items() if v != MAYBE]
    for r in data_rows:
        blanks = 0
        for field in YES_NO_QUESTIONS: # strict yes/no answers
            if r[field] in yes_no_options: 
                r[field] = ANSWER_OPTIONS[r[field]] 
            elif r[field] == "" and field in AUTOFILL_BLANK_NO:
                blanks += 1
                r[field] = NO
            else:
                raise Exception("Unexpected answer from %s to yes/no question '%s': got %s, expected %s" %(parse_name(r[EMAIL]), FIELD_HEADERS[field], r[field], " or ".join(yes_no_options)))
        for field in YES_MAYBE_NO_QUESTIONS: # yes/maybe/no answers
            if r[field] in ANSWER_OPTIONS:
                r[field] = ANSWER_OPTIONS[r[field]] 
            elif r[field] == "" and field in AUTOFILL_BLANK_NO:
                blanks += 1
                r[field] = NO
            else:
                raise Exception("Unexpected answer from %s to yes/maybe/no question '%s': got %s, expected %s" %(parse_name(r[EMAIL]), FIELD_HEADERS[field], r[field],  " or ".join(ANSWER_OPTIONS.keys())))
        if r[FULL_OR_HALF] != FULL and r[FULL_OR_HALF] != HALF:
            raise Exception("Unexpected answer from %s to '%s' question: got %s, expected %s or %s" %(parse_name(r[EMAIL]), FULL_OR_HALF, r[FULL_OR_HALF], FULL, HALF))
    return data_rows

def clean_pairing_requests(data_rows):
    data_out = {}
    names = [parse_name(r[EMAIL]) for r in data_rows]
    unrecognized_names = []
    for r in data_rows:
        requests = []
        for name in r[PAIR]:
            if name in names:
                requests.append(name)
            else:
                unrecognized_names.append(name)
        r[PAIR] = requests 
        r[NEW] = (r[NEW] == YES)
        data_out[parse_name(r[EMAIL])] = r 
    if len(unrecognized_names) != 0:
        print("WARNING: pairing requests contained some names that were not recognized and therefore ignored: %s.\nIf these are names for people who did in fact sign up, please change them in the data file to match the person's kerberos or email address." %", ".join(unrecognized_names))
    return data_out

def clean_data(data_rows):
    # check that all required fields exist
    for row in data_rows:
        for question in FIELD_HEADERS.values():
            if not question in row:
                raise Exception("Malformatted input; could not find the field %s. If the question name changed, you need to update the code with the new name (search the code for 'FIELD_HEADERS')." %question)
    # rename and prune fields
    data_rows = [{ field : row[FIELD_HEADERS[field]] for field in FIELD_HEADERS } for row in data_rows] 
    data_rows = reformat_multiple_choice(data_rows)
    data = clean_pairing_requests(data_rows)
    # make sure names are unique
    names = list(data.keys())
    for i in range(len(names)):
        for j in range(i+1, len(data)):
            if names[i] == names[j]:
                raise Exception("two occurrences of name %s (case-insensitive)", names[i])
    # if someone didn't say "yes" to either cooking or cleaning, then treat their "maybe" as "yes"
    for p in data:
        cook = data[p][COOK]
        clean = data[p][CLEAN]
        if cook != YES and clean != YES:
            if cook == MAYBE:
                data[p][COOK] = YES
            if clean == MAYBE:
                data[p][CLEAN] = YES
    return data

def parse_data(dataf):
    datar = csv.DictReader(dataf)
    data = []
    pair_header = FIELD_HEADERS[PAIR]
    for row in datar:
        if row[pair_header] == None:
            row[pair_header] = []
        else:
            row[pair_header] = [name.lower().strip() for name in row[pair_header].split(";") if name != ""]
        data.append(row)
    datac = clean_data(data)
    return datac

def warn_low_availability(data):
    for name in data:
        unavailable = list(filter(lambda t : data[name][t] == NO, SHIFT_TIMES))
        if len(unavailable) > len(SHIFT_TIMES) * (2.0 / 3):
            print("WARNING: %s is unavailable for > 2/3 of available shift times (%s out of %s)" %(name, len(unavailable), len(SHIFT_TIMES)))

def get_stats(data, field):
    yes = 0
    maybe = 0
    for name in data:
        value = 1 if data[name][FULL_OR_HALF] == HALF else 2
        if data[name][field] == YES:
            yes += value
        elif data[name][field] == MAYBE:
            maybe += value
    return yes, maybe

def display_stats(data):
    print("Stats (full mealplanners count as 2):")
    print("Cooking (%s shifts) -- %s yes, %s maybe" %(len([s for s in Schedule.shifts if s.is_cooking]), *get_stats(data, COOK)))
    print("Cleaning (%s shifts) -- %s yes, %s maybe" %(len([s for s in Schedule.shifts if not s.is_cooking]), *get_stats(data, CLEAN)))
    print("Big cooking (%s shifts) -- %s yes, %s maybe" %(len([s for s in Schedule.shifts if s.is_big_cooking]), *get_stats(data, BIGCOOK)))
    nshifts_possible = sum([(1 if data[name][FULL_OR_HALF] == HALF else 2) for name in data])
    print("%s shifts are needed. There are enough people to fill %s shifts." %(len(Schedule.shifts), nshifts_possible))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python schedule.py [data file]")
        sys.exit()

    dataf = open(sys.argv[1])
    data = parse_data(dataf)
    print("") # puts space between warnings
    warn_low_availability(data)
    print("")
    display_stats(data)
    print("")
    
    loop = Loop(data)
    try:
        loop.cmdloop(intro=Loop.welcome())
    except Exception as e:
        loop.autosave()
        raise e # still raise the exception, just autosave first
    except KeyboardInterrupt:
        loop.autosave()
        sys.exit()


# TODO: suggest switches that would make everyone happier (maybe only at the end, or when explicitly requested)
