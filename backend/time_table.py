import numpy as np
import random
from collections import defaultdict
from tabulate import tabulate
import copy
import json

data_dict = {
    "num_days": None,
    "periods_per_day": None,
    "lunch_after_period": None,
    "classes": [],
    "subjects": {},
    "teachers": {},
    "class_requirements": {}
}

def get_teacher_details():
    """Get teacher details from user input"""
    teachers = {}
    teacher_names = {}
    
    num_teachers = int(input("Enter the number of teachers: "))
    
    for i in range(num_teachers):
        print(f"\nEnter details for teacher {i+1}:")
        code = input("Enter teacher code (e.g., AP001): ")
        name = input("Enter teacher name: ")
        print("Enter subjects taught (comma-separated, e.g., MATH,PHYSICS): ")
        subjects = [s.strip() for s in input().split(',')]
        
        teachers[code] = subjects
        teacher_names[code] = name
    
    return teachers, teacher_names

def display_timetable(timetable_dict, periods_per_day, num_days):
    """
    Display the generated timetable in a readable format using the first 'num_days' of the week.
    """
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days = all_days[:num_days]
    headers = ['Day'] + [f'Period {i+1}' for i in range(periods_per_day)]
    
    for class_name, timetable in timetable_dict.items():
        print(f"\nTimetable for Class {class_name}:")
        table_data = []
        for day_idx, day in enumerate(days):
            row = [day]
            for period in range(periods_per_day):
                subject = timetable[day_idx, period]
                row.append(subject if subject else '-')
            table_data.append(row)
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

class MultiClassTimetableEnvironment:
    def __init__(self, days, periods_per_day, lunch_after_period, classes, teachers, teacher_names, subjects, class_requirements):
        # Here, 'days' is an integer representing the number of days used (from Monday onward)
        self.days = days
        self.periods_per_day = periods_per_day
        self.lunch_after_period = lunch_after_period
        self.classes = classes
        self.teachers = teachers
        self.teacher_names = teacher_names  # Teacher names dictionary
        self.subjects = subjects
        self.class_requirements = class_requirements
        
        self.max_consecutive_same_subject = 2  # Maximum consecutive periods for same subject
        self.preferred_lab_periods = [0, 2]  # Preferred periods for lab sessions (before and after lunch)
        
        self._validate_lab_requirements()
        self._validate_teacher_assignments()
        
        self.timetable = self._create_empty_timetable()
        self.current_position = (0, 0, classes[0])
        self.best_timetable = None
        self.best_score = float('-inf')

    def _validate_lab_requirements(self):
        """Ensure all lab subjects have even number of hours"""
        for class_name, requirements in self.class_requirements.items():
            for subject, req_dict in requirements.items():
                if subject in self.subjects and self.subjects[subject]['is_lab']:
                    lectures = req_dict['lectures']
                    if lectures % 2 != 0:
                        raise ValueError(f"Lab subject {subject} for class {class_name} must have even number of lectures. Current: {lectures}")

    def _create_empty_timetable(self):
        """Create an empty timetable for all classes with lunch break.
           The timetable has dimensions (num_days x (periods_per_day + 1))"""
        timetables = {}
        for class_name in self.classes:
            timetable = np.zeros((self.days, self.periods_per_day + 1), dtype=object)  # +1 for lunch break
            # Mark lunch break slots
            for day in range(self.days):
                timetable[day, self.lunch_after_period] = 'LUNCH'
            timetables[class_name] = timetable
        return timetables
    
    def _validate_teacher_assignments(self):
        """Validate that all subjects have valid teacher assignments"""
        for class_name, requirements in self.class_requirements.items():
            for subject, req_dict in requirements.items():
                if subject != 'teacher_code':
                    teacher_code = req_dict['teacher_code']
                    if teacher_code not in self.teachers:
                        raise ValueError(f"Invalid teacher code {teacher_code} for {subject} in class {class_name}")
                    if subject not in self.teachers[teacher_code]:
                        raise ValueError(f"Teacher {teacher_code} is not qualified to teach {subject}")

    def _check_daily_load(self, day, teacher_id):
        """Check if teacher has exceeded maximum daily load"""
        max_daily_load = 6  # Maximum periods per day for a teacher
        count = 0
        for class_name in self.classes:
            for period in range(self.periods_per_day + 1):
                current_slot = self.timetable[class_name][day, period]
                if current_slot and current_slot != 'LUNCH':
                    slot_teacher = self.class_requirements[class_name][current_slot]['teacher_code']
                    if slot_teacher == teacher_id:
                        count += 1
        return count < max_daily_load

    def _check_consecutive_subjects(self, day, period, subject, current_class):
        """Check if subject would create too many consecutive periods"""
        if period > 0 and period < self.periods_per_day:
            consecutive_count = 1
            # Check backwards
            p = period - 1
            while p >= 0 and self.timetable[current_class][day, p] == subject:
                consecutive_count += 1
                p -= 1
            # Check forwards
            p = period + 1
            while p < self.periods_per_day and self.timetable[current_class][day, p] == subject:
                consecutive_count += 1
                p += 1
            return consecutive_count <= self.max_consecutive_same_subject
        return True

    def _check_constraints(self, day, period, subject, current_class):
        """Enhanced constraint checking"""
        if period == self.lunch_after_period:
            return False
            
        if self.subjects[subject]['is_lab']:
            return self._check_lab_constraints(day, period, subject, current_class)
            
        teacher_id = self.class_requirements[current_class][subject]['teacher_code']
        
        # Basic teacher availability check
        if not self._check_teacher_availability(day, period, teacher_id):
            return False
            
        # Check daily teacher load
        if not self._check_daily_load(day, teacher_id):
            return False
            
        # Check consecutive subjects
        if not self._check_consecutive_subjects(day, period, subject, current_class):
            return False
            
        # Check subject distribution
        if not self._check_subject_distribution(day, subject, current_class):
            return False
        
        return True

    def _check_teacher_availability(self, day, period, teacher_id):
        """Check if teacher is available"""
        for class_name in self.classes:
            current_slot = self.timetable[class_name][day, period]
            if current_slot and current_slot != 'LUNCH':
                slot_teacher = self.class_requirements[class_name][current_slot]['teacher_code']
                if slot_teacher == teacher_id:
                    return False
        return True

    def _check_subject_distribution(self, day, subject, current_class):
        """Check if subject is well-distributed across the day"""
        max_per_day = 2  # Maximum occurrences of a subject per day
        count = 0
        for period in range(self.periods_per_day + 1):
            if self.timetable[current_class][day, period] == subject:
                count += 1
        return count < max_per_day
    
    def _check_lab_constraints(self, day, period, subject, current_class):
        """Check if a lab can be scheduled at this position"""
        if not self.subjects[subject]['is_lab']:
            return True
                
        # Check if we have enough continuous periods
        if period >= self.periods_per_day or period == self.lunch_after_period - 1:
            return False
                
        # Check if next period is free and not lunch
        next_period = period + 1
        if next_period == self.lunch_after_period or self.timetable[current_class][day, next_period]:
            return False
                
        teacher_id = self.class_requirements[current_class][subject]['teacher_code']
            
        # Check if teacher is available in both periods
        for class_name in self.classes:
            for p in [period, next_period]:
                current_slot = self.timetable[class_name][day, p]
                if current_slot and current_slot != 'LUNCH':
                    slot_teacher = self.class_requirements[class_name][current_slot]['teacher_code']
                    if slot_teacher == teacher_id:
                        return False
        # New constraint: Check number of labs for this subject on this day
        lab_count = 0
        for p in range(self.periods_per_day + 1):
            if self.timetable[current_class][day, p] == subject:
                if p == 0 or self.timetable[current_class][day, p-1] != subject:
                    lab_count += 1
        
        if lab_count >= 2:
            return False
                    
        return True
    
    def _get_remaining_classes(self):
        remaining = {}
        for class_name in self.classes:
            scheduled_classes = defaultdict(int)
            for day in range(self.days):
                for period in range(self.periods_per_day + 1):  # +1 for lunch
                    if self.timetable[class_name][day, period] and self.timetable[class_name][day, period] != 'LUNCH':
                        subject = self.timetable[class_name][day, period]
                        if self.subjects[subject]['is_lab']:
                            if period == 0 or self.timetable[class_name][day, period-1] != subject:
                                scheduled_classes[subject] += 2
                        else:
                            scheduled_classes[subject] += 1
            
            remaining[class_name] = {}
            for subject in self.class_requirements[class_name]:
                if subject != 'teacher_code':
                    required = self.class_requirements[class_name][subject]['lectures']
                    remaining[class_name][subject] = required - scheduled_classes[subject]
        return remaining
    
    def calculate_timetable_score(self):
        """Calculate a score for the current timetable based on various criteria"""
        score = 0
        
        for class_name in self.classes:
            subject_distribution = defaultdict(list)
            for day in range(self.days):
                for period in range(self.periods_per_day + 1):
                    subject = self.timetable[class_name][day, period]
                    if subject and subject != 'LUNCH':
                        subject_distribution[subject].append(day)
            
            for subject, days in subject_distribution.items():
                unique_days = len(set(days))
                score += unique_days * 2
            
        for class_name in self.classes:
            for day in range(self.days):
                for period in self.preferred_lab_periods:
                    subject = self.timetable[class_name][day, period]
                    if subject and subject != 'LUNCH' and self.subjects[subject]['is_lab']:
                        score += 5
        
        return score
    
    def reset(self):
        """Reset the environment to initial state"""
        self.timetable = self._create_empty_timetable()
        self.current_position = (0, 0, self.classes[0])
        return self._get_state()
    
    def _get_state(self):
        """Get current state of the environment"""
        return {
            'position': self.current_position,
            'timetable': {k: v.copy() for k, v in self.timetable.items()},
            'remaining_classes': self._get_remaining_classes()
        }
    
    def step(self, action):
        day, period, current_class = self.current_position
        reward = 0
        done = False
        
        if period == self.lunch_after_period:
            period += 1
            
        if self.subjects[action]['is_lab']:
            if self._check_lab_constraints(day, period, action, current_class):
                self.timetable[current_class][day, period] = action
                self.timetable[current_class][day, period + 1] = action
                reward = 1
                period += 1
            else:
                reward = -1
        else:
            if self._check_constraints(day, period, action, current_class):
                self.timetable[current_class][day, period] = action
                reward = 1
            else:
                reward = -1
        
        class_idx = self.classes.index(current_class)
        class_idx += 1
        if class_idx >= len(self.classes):
            class_idx = 0
            period += 1
            if period >= self.periods_per_day + 1:  # +1 for lunch
                period = 0
                day += 1
        
        if day >= self.days:
            done = True
            remaining = self._get_remaining_classes()
            if all(all(v == 0 for v in class_reqs.values()) 
                   for class_reqs in remaining.values()):
                reward += 100
                
        self.current_position = (day, period, self.classes[class_idx])
        return self._get_state(), reward, done
    
    def display_detailed_timetable(self):
        """
        Display a detailed version of the timetable with teacher information,
        using the first 'self.days' of the week.
        """
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days = all_days[:self.days]
        periods = [f'Period {i+1}' for i in range(self.periods_per_day + 1)]
        
        for class_name in self.classes:
            print(f"\n{'='*80}")
            print(f"Timetable for Class {class_name}")
            print(f"{'='*80}")
            
            table_data = []
            for day_idx, day in enumerate(days):
                row = [day]
                for period in range(self.periods_per_day + 1):
                    subject = self.timetable[class_name][day_idx, period]
                    if subject == 'LUNCH':
                        cell = 'LUNCH BREAK'
                    elif subject:
                        teacher_code = self.class_requirements[class_name][subject]['teacher_code']
                        cell = f"{subject}\n({teacher_code})"
                    else:
                        cell = '-'
                    row.append(cell)
                table_data.append(row)
            
            print(tabulate(table_data, headers=['Day'] + periods, tablefmt='grid'))
            print(f"\nTeacher Allocation for Class {class_name}:")
            for subject in self.class_requirements[class_name]:
                if subject != 'teacher_code':
                    teacher_code = self.class_requirements[class_name][subject]['teacher_code']
                    teacher_name = self.teacher_names[teacher_code]
                    print(f"- {subject}: {teacher_code} - {teacher_name}")

class QLearningAgent:
    def __init__(self, action_space, learning_rate=0.1, discount_factor=0.95, epsilon=0.3):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.action_space = action_space
        
    def get_state_key(self, state):
        """Convert state to a string key for Q-table"""
        if state and 'position' in state:
            return str(state['position'])
        return "default"
        
    def get_action(self, state, valid_actions):
        if not valid_actions:
            return None
            
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        
        state_key = self.get_state_key(state)
        q_values = {action: self.q_table[state_key][action] for action in valid_actions}
        
        if all(value == 0 for value in q_values.values()):
            return random.choice(valid_actions)
        
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def update(self, state, action, reward, next_state):
        if not state or not next_state or not action:
            return
            
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        next_q_values = [self.q_table[next_state_key][a] for a in self.action_space]
        next_max_q = max(next_q_values) if next_q_values else 0
        
        current_q = self.q_table[state_key][action]
        new_q = current_q + self.lr * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state_key][action] = new_q
        
def train_timetable_generator(env, agent, episodes=1000):
    best_reward = float('-inf')
    best_timetable = None
    best_score = float('-inf')
    
    initial_epsilon = 0.3
    final_epsilon = 0.01
    epsilon_decay = (initial_epsilon - final_epsilon) / episodes
    
    for episode in range(episodes):
        try:
            state = env.reset()
            total_reward = 0
            done = False
            
            agent.epsilon = max(initial_epsilon - episode * epsilon_decay, final_epsilon)
            
            while not done:
                if not state:
                    break
                    
                current_class = state['position'][2]
                valid_actions = [subject for subject, remaining in state['remaining_classes'][current_class].items() if remaining > 0]
                
                if not valid_actions:
                    break
                    
                action = agent.get_action(state, valid_actions)
                if not action:
                    break
                    
                next_state, reward, done = env.step(action)
                agent.update(state, action, reward, next_state)
                state = next_state
                total_reward += reward
                
                if done:
                    timetable_score = env.calculate_timetable_score()
                    reward += timetable_score
                    
                    if timetable_score > best_score:
                        best_score = timetable_score
                        best_timetable = copy.deepcopy(env.timetable)
            
            current_score = env.calculate_timetable_score()
            if current_score > best_score:
                best_score = current_score
                best_timetable = copy.deepcopy(env.timetable)
            
            if total_reward > best_reward:
                best_reward = total_reward
                
            if episode % 100 == 0:
                print(f"Episode {episode}, Best Reward: {best_reward:.2f}, Best Score: {best_score:.2f}")
                
        except Exception as e:
            print(f"Error in episode {episode}: {str(e)}")
            continue
    
    return best_timetable if best_timetable is not None else env.timetable

if __name__ == "__main__":
    try:
        # Ask user for the number of days for the timetable (max 7)
        num_days = int(input("Enter number of days for the timetable (1 to 7): "))
        if num_days > 7:
            num_days = 7
        elif num_days < 1:
            num_days = 1
        
        periods_per_day = int(input("Enter number of periods per day: "))
        lunch_after_period = int(input("Enter after which period lunch break should be scheduled (e.g., 2 for after 2nd period): "))
        
        # Get class information
        num_classes = int(input("Enter number of classes: "))
        classes = []
        for i in range(num_classes):
            class_name = input(f"Enter name for class {i+1}: ")
            classes.append(class_name)
        
        # Define subjects
        print("\nEnter subject details:")
        subjects = {}
        num_subjects = int(input("Enter number of subjects: "))
        for i in range(num_subjects):
            subject_name = input(f"Enter name for subject {i+1}: ")
            is_lab = input(f"Is {subject_name} a lab subject? (yes/no): ").lower() == 'yes'
            subjects[subject_name] = {'is_lab': is_lab}
        
        # Get teacher details
        print("\nEnter teacher details:")
        teachers, teacher_names = get_teacher_details()
        
        # Get class requirements
        class_requirements = {}
        print("\nEnter class requirements:")
        for class_name in classes:
            print(f"\nFor class {class_name}:")
            class_requirements[class_name] = {}
            
            for subject in subjects:
                print(f"\nFor subject {subject}:")
                teacher_code = input(f"Enter teacher code who will teach {subject}: ")
                while teacher_code not in teachers or subject not in teachers[teacher_code]:
                    print(f"Error: Teacher {teacher_code} cannot teach {subject}. Available teachers:")
                    for t_code, t_subjects in teachers.items():
                        if subject in t_subjects:
                            print(f"- {t_code} ({teacher_names[t_code]})")
                    teacher_code = input(f"Enter valid teacher code for {subject}: ")
                
                lectures = int(input(f"Enter number of lectures for {subject}: "))
                if subjects[subject]['is_lab'] and lectures % 2 != 0:
                    print("Warning: Lab subjects must have even number of lectures.")
                    lectures = int(input(f"Enter even number of lectures for {subject}: "))
                
                class_requirements[class_name][subject] = {
                    'teacher_code': teacher_code,
                    'lectures': lectures
                }
        
        # Create and train the model
        env = MultiClassTimetableEnvironment(
            num_days, periods_per_day, lunch_after_period, classes, 
            teachers, teacher_names, subjects, class_requirements
        )
        agent = QLearningAgent(list(subjects.keys()))
        
                # ==== DATA COLLECTION SECTION START ====
        # Populate basic parameters
        data_dict["num_days"] = num_days
        data_dict["periods_per_day"] = periods_per_day
        data_dict["lunch_after_period"] = lunch_after_period
        data_dict["classes"] = classes.copy()

        # Populate subjects
        for subj_name, subj_details in subjects.items():
            data_dict["subjects"][subj_name] = {
                "is_lab": subj_details['is_lab']
            }

        # Populate teachers - FIXED VERSION
        teacher_codes = list(teachers.keys())  # Get codes from teachers dict
        for code in teacher_codes:
            data_dict["teachers"][code] = {
                "name": teacher_names[code],
                "subjects": teachers[code].copy()  # teachers dict contains subjects
            }


        # Populate class requirements - FIXED VERSION
        for cls in classes:
            data_dict["class_requirements"][cls] = {}
            for subj in class_requirements[cls]:
                data_dict["class_requirements"][cls][subj] = {
                    "teacher": class_requirements[cls][subj]['teacher_code'],  # Changed from 'teacher'
                    "lectures": class_requirements[cls][subj]['lectures']  # Changed from 'total_lectures'
                }


        # Print collected data
        print("\n" + "="*60)
        print("COLLECTED INPUT DATA STRUCTURE:")
        print(json.dumps(data_dict, indent=2))
        print("="*60 + "\n")
        # ==== DATA COLLECTION SECTION END ====

        print("\nTraining the model...")
        best_timetable = train_timetable_generator(env, agent, episodes=1000)
        
        if best_timetable is not None:
            env.timetable = best_timetable
            env.display_detailed_timetable()
        else:
            print("Failed to generate a valid timetable. Please try again.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()