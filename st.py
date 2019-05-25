import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib import style

conn = sqlite3.connect('study.db')
c = conn.cursor()

style.use('ggplot')
now = datetime.datetime.now()
LARGE_FONT = ('Garamond', 18)
NORMAL_FONT = ('Garamond', 12)
goal = [] #This will update and keep track of the user's goal.


class NoInputError(Exception):
    '''Exception for input of 0 hours and 0 minutes.'''
    def __init__(self):
        Exception.__init__(self)


class StudyTracker(tk.Tk):
    '''This class sets up most of the backend'''
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, 'Study Tracker')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Pageone, Pagetwo, Pagethree): #this contains all of the main windows.
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.create_table()
        self.show_frame(Pageone)

    def create_table(self):
        '''Creates the only table necessary for the app'''
        c.execute("CREATE TABLE IF NOT EXISTS study_sessions(graph_date TEXT, date TEXT, hours INTEGER, minutes INTEGER, comp_time INTEGER, goal INTEGER)")
        c.execute("SELECT goal FROM study_sessions")
        if len(c.fetchall()) == 0:
            with conn:
                c.execute('INSERT INTO study_sessions(graph_date, date, hours, minutes, comp_time, goal) VALUES (?, ?, ?, ?, ?, ?)', ('-', '-', 0, 0, 0, 50))
        else:
            pass

    def show_frame(self, controller):
        '''Brings the desired page in front of the other pages'''
        frame = self.frames[controller]
        frame.tkraise()


class Pageone(tk.Frame):
    '''Welcome Page'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        welcome_lbl = tk.Label(self, text='Welcome to Study Tracker', font=LARGE_FONT).pack()
        info_lbl = tk.Label(self, text='Learn any topic at your own pace!\n\n', font=NORMAL_FONT).pack()
        s1 = tk.Label(self, text="\n").pack()
        calc_page_btn1 = ttk.Button(self, text='Study Calculator', command=lambda: self.calc_page(controller))
        calc_page_btn1.pack()
        s2 = tk.Label(self, text="\n").pack()
        track_page_btn1 = ttk.Button(self, text='Track your Progress', command=lambda: self.track_page(controller))
        track_page_btn1.pack()
        s3 = tk.Label(self, text="\n").pack()
        exit_btn = ttk.Button(self, text='Exit', command=quit).pack()

    def set_goal(self):
        '''This will loop into the goal list, establishing a default goal the user has already saved'''
        goal.clear()
        c.execute("SELECT goal FROM study_sessions")
        for row in c.fetchall():
            goal.append(row[0])

    def calc_page(self, controller):
        '''Fills the goal list as another page is raised infront'''
        self.set_goal()
        controller.show_frame(Pagetwo)

    def track_page(self, controller):
        self.set_goal()
        controller.show_frame(Pagethree)


class Pagetwo(tk.Frame):
    '''Study calculator page'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.set_goals = tk.IntVar()
        self.hours = tk.IntVar()
        self.minutes = tk.IntVar()

        q1 = tk.Label(self, text='How many hours have you studied?\n', font=NORMAL_FONT).pack()
        self.hrs_input = tk.Entry(self, textvariable=self.hours)
        self.hrs_input.pack()
        q2 = tk.Label(self, text='AND/OR, how many minutes did you study for?\n', font=NORMAL_FONT).pack()
        self.mins_input = tk.Entry(self, textvariable=self.minutes)
        self.mins_input.pack()
        calc_btn = ttk.Button(self, text='Calculate', command=self.display).pack()
        track_page_btn2 = ttk.Button(self, text='Track your Progress', command=lambda: controller.show_frame(Pagethree)).pack()
        home_btn = ttk.Button(self, text='Back to Home', command=lambda: controller.show_frame(Pageone)).pack()
        clear_data_btn = ttk.Button(self, text='Clear Data', command=self.clear).pack()
        goal_change_lbl = tk.Label(self, text='\nChange your goal here!\n').pack()
        self.set_goal = tk.Entry(self, textvariable=self.set_goals)
        self.set_goal.pack()
        goal_change_btn = ttk.Button(self, text='Change', command=self.goal_change).pack()
        self.total_sessions = tk.Label(self, text="", font=NORMAL_FONT)
        self.total_sessions.pack()

    def clear(self):
        '''Clears all data, but keeps the goal integer'''
        try:
            with conn:
                c.execute('DELETE FROM study_sessions')
                c.execute('INSERT INTO study_sessions (graph_date, date, hours, minutes, comp_time, goal) VALUES (?, ?, ?, ?, ?, ?)', ('-', '-', 0, 0, 0, goal[-1]))
        except IndexError:
            pass

    def Reached_Goal_window(self):
        '''Creates a popup window'''
        root2 = tk.Toplevel(self.master)
        Reached_Goal(root2)

    def goal_change(self):
        '''Changes the user's goal'''
        new_goal = int(self.set_goal.get())
        with conn:
            c.execute('UPDATE study_sessions SET goal=? WHERE goal=?', (new_goal, goal[-1]))
        goal.clear()
        goal.append(new_goal) #establishes a new default goal, from user input
        self.set_goal.delete(0, 'end')
        self.set_goals.set(0)

    def specifictime(self, x, date):
        '''Returns a string of the time in which you studied, with the hour being parameter x'''
        if x >= 3 and x < 11:
            return(date + ', in the morning')
        elif x >=11 and x < 13:
            return(date + ', at around noon')
        elif x >= 13 and x < 18:
            return(date + ', in the afternoon')
        elif x >=18 and x < 21:
            return(date + ', in the evening')
        elif x >= 21 and x < 24:
            return(date + ', at night')
        elif x >= 0 and x < 3:
            return(date + ', in the middle of the night')

    def hrs_mins_lists(self, hrs, mins, hrs_list, mins_list):
        '''Appends the lists with study-time data'''
        hrs_list.append(hrs)
        mins_list.append(mins)
        c.execute('SELECT hours, minutes FROM study_sessions')
        for row in c.fetchall():
            hrs_list.append(row[0])
            mins_list.append(row[1])

    def date_string(self):
        '''Returns the correct string for specifictime function'''
        date1 = datetime.datetime.strftime(now, '%b %d, %Y') #ex. Jan 30, 2019
        date2 = datetime.datetime.strftime(now, '%H') #ex. if it's 4:35pm, it will only return 16
        datehour = int(date2) #we only need to extract the hour for parameter
        return self.specifictime(datehour, date1)

    def insert_clear(self, total_hrs, total_mins, math_mins, graph_date, date, hrs, mins):
        math_hrs = sum(total_hrs) * 60 #converting into minutes for swift calculation
        math_mins.append(sum(total_mins))
        math_mins.append(math_hrs)
        all_mins = sum(math_mins) #will be stored in 'comp_time' column and will be used later in the app
        with conn:
            c.execute('INSERT INTO study_sessions (graph_date, date, hours, minutes, comp_time, goal) VALUES (?, ?, ?, ?, ?, ?)',
            (graph_date, date, hrs, mins, all_mins, goal[-1]))
        total_mins.clear()
        total_hrs.clear()
        math_mins.clear()

    def study_calc_1(self):
        '''Prepares new data for study_calc_2 function'''
        try:
            total_hrs = [] #all hours from .db file will go in here
            total_mins = [] #all minutes from individual study sessions will go in here
            math_mins = [] #data put here is to only for calculations
            hrs = int(self.hrs_input.get())
            mins = int(self.mins_input.get())
            if hrs == 0 and mins == 0:
                raise NoInputError()
            if len(goal) == 0:
                raise IndexError
            graph_date = datetime.datetime.strftime(now, '%b %d, (%H)')
            date = self.date_string()
            self.hrs_mins_lists(hrs, mins, total_hrs, total_mins)
            self.insert_clear(total_hrs, total_mins, math_mins, graph_date, date, hrs, mins)
        except ValueError:
            pass
        except NoInputError:
            pass

    def study_calc_2(self):
        '''Returns a string of current hours and minutes studied'''
        try:
            self.study_calc_1()
            times = []
            c.execute('SELECT comp_time FROM study_sessions')
            for row in c.fetchall():
                times.append(row[0])
            time = max(times)
            hr = time // 60
            min = time % 60
            if hr >= goal[-1]:
                self.Reached_Goal_window() #popup window
                return("\n\nYou've studied for {} hours and {} minutes out of {} hours!". format(hr, min, goal[-1]))
            else:
                return("\n\nYou've studied for {} hour(s) and {} minutes out of {} hours!". format(hr, min, goal[-1]))
        except ValueError:
            pass


    def clear_time(self):
        '''Clears the entry boxes'''
        self.hrs_input.delete(0, 'end')
        self.mins_input.delete(0, 'end')
        self.hours.set(0)
        self.minutes.set(0)

    def display(self):
        '''Shows the string returned in study_calc_2 function'''
        try:
            if len(goal) == 0:
                raise IndexError
            reveal = self.study_calc_2()
            self.total_sessions.configure(text=reveal)
            self.clear_time()
        except IndexError:
            self.total_sessions.configure(text="\n\nEnter a goal")


class Pagethree(tk.Frame):
    '''Track progress page'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        view_txt_lbl = tk.Label(self, text='View your progress in text form!\n', font=NORMAL_FONT).pack()
        view_txt_btn = ttk.Button(self, text='Progress Info (Text)', command=self.display_progress).pack()
        view_graph_lbl = tk.Label(self, text='\nSee your progress over time!\n', font=NORMAL_FONT).pack()
        view_graph_btn = ttk.Button(self, text='Progress Graph', command=self.graph).pack()
        back_lbl = tk.Label(self, text='\nWant to study some more?\n', font=NORMAL_FONT).pack()
        back_calc_btn = ttk.Button(self, text='Study Calculator', command=lambda: controller.show_frame(Pagetwo)).pack()
        back_home_btn = ttk.Button(self, text='Back to Home Page', command=lambda: controller.show_frame(Pageone)).pack()
        scroll = tk.Scrollbar(self)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_text = tk.Text(self, height=10, width=50)
        self.view_text.config(yscrollcommand=scroll.set, state="disabled")
        scroll.config(command=self.view_text.yview)
        self.view_text.pack()

    def print_progress(self):
        '''Generator for returning strings of study progress'''
        try:
            dates = []
            hrs = []
            mins = []
            c.execute('SELECT date, hours, minutes FROM study_sessions')
            for row in c.fetchall():
                dates.append(row[0])
                hrs.append(row[1])
                mins.append(row[2])
            del (dates[0], hrs[0], mins[0])
            for d, h, m in zip(dates, hrs, mins):
                yield('On {}, you had a study session for {} hour(s) and {} minutes.\n\n'.format(d, h, m))
        except IndexError:
            pass

    def display_progress(self):
        '''Displays each string in the generator in the tkinter textbox'''
        self.view_text.config(state="normal")
        self.view_text.delete('1.0', tk.END) #clears the textbox
        for text in [i for i in self.print_progress()]:
            self.view_text.insert(tk.INSERT, text)
        self.view_text.config(state="disabled")

    def display_graph(self, x, y):
        '''Graph set up'''
        plt.xlabel('Number of Study Sessions')
        plt.ylabel('Minutes of Study Sessions')
        plt.title('Your Study Habits......VISUALIZED!!!!!')
        plt.plot(x, y)
        plt.xticks(fontsize=8, rotation=5)
        plt.show()

    def real_x(self, list):
        x = []
        for i in range(0, len(list)):
            x.append(i)
        return x

    def graph(self):
        '''Extracts and graphs study session data'''
        pre_x = []
        hours = []
        mins = []
        c.execute('SELECT graph_date, hours, minutes FROM study_sessions')
        for row in c.fetchall():
            pre_x.append(row[0]) #dates
            hours.append(row[1])
            mins.append(row[2])
        more_mins = [i*60 for i in hours] #convert hours into minutes, while keeping list format
        y_axis = [p + q for p, q in zip(mins, more_mins)] #only minutes
        x_axis = self.real_x(pre_x)
        self.display_graph(x_axis, y_axis)


class Reached_Goal():
    '''A pop-up window, giving the user the choice to continue with a higher goal or clear their data'''
    def __init__(self, master):
        self.master = master
        self.master.geometry('420x175')
        self.master.title('Study Tracker')

        reached_goal = 'You have reached your goal!\n\nWould you like to continue with a higher goal or clear your data?'
        self.completed = tk.Label(self.master, text=reached_goal, font=NORMAL_FONT)
        self.completed.grid(row=0, column=2)

        self.continue_btn = ttk.Button(self.master, text='Continue w/ higher goal', command=master.withdraw).grid(row=3, column=2)
        self.clear_btn = ttk.Button(self.master, text ='Clear Data', command=self.clear).grid(row=4, column=2)

    def clear(self):
        '''Clears data in .db file, but keeps default goal'''
        with conn:
            c.execute('DELETE FROM study_sessions')
            c.execute('INSERT INTO study_sessions (graph_date, date, hours, minutes, comp_time, goal) VALUES (?, ?, ?, ?, ?, ?)', ('-', '-', 0, 0, 0, goal[-1]))
        self.completed.configure(text='***We shall start again! Exit out of this window')


if __name__ == "__main__":
    app = StudyTracker()
    app.mainloop()
    c.close()
    conn.close()
