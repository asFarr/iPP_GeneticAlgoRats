"""
Genetic Algorithm Practice: Breeding Rats v0.2 - by asFarr : 2/25/22

Project is based on a chapter from Impractical Python Projects by: Lee Vaughan

Implements a simple genetic algorithm to 'breed rats' as a demonstration of refining labelled 
and weighted data stochastically over successive epochs to fit to parameterized constraints.

...At least that's my high-level takeaway, though I fully admit I might have butchered it in an attempt at brevity. 

I have departed from the scope of the original book project in order to explore TKinter, TTK, and Matplotlib 
to study applying those modules for UI-driven data visualization. 

"""

import time
import statistics as stat
import random as rn
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
matplotlib.use("TkAgg")

# WINDOW CONSTANTS
LARGE_FONT = ("Verdana", 12)
SMALL_FONT = ("Verdana", 8)

# ALGORITHM CONSTANTS (weights are in grams)
GOAL = 65771
NUM_RATS = 20
INITIAL_MIN_WT = 200
INITIAL_MAX_WT = 600
INITIAL_MODE_WT = 300
MUTATE_ODDS = 0.01
MUTATE_MIN = 0.1
MUTATE_MAX = 1.25
LITTER_SIZE = 16
LITTERS_PER_YEAR = 10
GENERATION_LIMIT = 500

# Global Scope configurations
style.use('ggplot')


class Results:

    def __init__(self, *args, **kwargs):
        self.avg_weight = []
        self.fit_graph = []
        self.gens = []
        self.yrs = None
        self.dur = None
        self.pars = None
        self.popfit = None

    def fill(self, output):
        self.avg_weight = output[0]
        self.fit_graph = output[1]
        self.gens = output[2]
        self.yrs = output[3]
        self.dur = output[4]
        self.pars = output[5]
        self.popfit = output[6]


res = Results()
f1 = Figure(figsize=(5, 3), dpi=100)
a1 = f1.add_subplot(111)
f2 = Figure(figsize=(5, 3), dpi=100)
a2 = f2.add_subplot(111)

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="favicon.ico")
        tk.Tk.wm_title(self, "Genetic Algorithm v0.2 -- written by Alex F")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (ExperimentPage, HelpPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ExperimentPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class ExperimentPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        dur = tk.StringVar(self)
        gens = tk.StringVar(self)
        yrs = tk.StringVar(self)
        avgwt = tk.StringVar(self)
        pars = tk.StringVar(self)
        popfit = tk.StringVar(self)

        label1 = ttk.Label(self, text="Genetic Algorithm GUI v0.2", font=LARGE_FONT)
        label1.pack(pady=10, padx=10)
        label2 = ttk.Label(self, text=
                           "An exercise in integrating TKinter, TTK and Matplotlib for a more elegant perspective.",
                           font=SMALL_FONT)
        label2.pack(pady=10, padx=10)

        aframe = ttk.Frame(self)
        aframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas1 = FigureCanvasTkAgg(f1, aframe)
        canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar1 = NavigationToolbar2Tk(canvas1, aframe)
        toolbar1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        bframe = ttk.Frame(self)
        bframe.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        canvas2 = FigureCanvasTkAgg(f2, bframe)
        canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar2 = NavigationToolbar2Tk(canvas2, bframe)
        toolbar2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        statframeleft = ttk.LabelFrame(self, text="Statistics")
        statframeleft.pack(side=tk.LEFT)

        durationframe = ttk.LabelFrame(statframeleft, text="Duration of Test: ")
        durationframe.pack(side=tk.TOP, fill=tk.BOTH,  expand=True)

        durationlabel = ttk.Label(durationframe, textvar=dur)
        durationlabel.pack()

        generationsframe = ttk.LabelFrame(statframeleft, text="Number of Generations: ")
        generationsframe.pack(side=tk.TOP, fill=tk.BOTH,  expand=True)

        generationslabel = ttk.Label(generationsframe, textvar=gens)
        generationslabel.pack()

        yrsframe = ttk.LabelFrame(statframeleft, text="Number of Years: ")
        yrsframe.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        yrslabel = ttk.Label(yrsframe, textvar=yrs)
        yrslabel.pack()
        # Change these over to new values to track
        statframeright = ttk.LabelFrame(self, text="Statistics")
        statframeright.pack(side=tk.RIGHT)

        parwgtframe = ttk.LabelFrame(statframeright, text="Average Final Weight: ")
        parwgtframe.pack(side=tk.TOP, fill=tk.BOTH,  expand=True)

        parwgtlabel = ttk.Label(parwgtframe, textvar=pars)
        parwgtlabel.pack()

        popfitframe = ttk.LabelFrame(statframeright, text="Initial Population Fitness: ")
        popfitframe.pack(side=tk.TOP, fill=tk.BOTH,  expand=True)

        popfitlabel = ttk.Label(popfitframe, textvar=popfit)
        popfitlabel.pack()

        avgwtframe = ttk.LabelFrame(statframeright, text="Initial Average Weight: ")
        avgwtframe.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        avgwtlabel = ttk.Label(avgwtframe, wraplength=256, textvar=avgwt)
        avgwtlabel.pack()

        buttonframe = tk.Frame(self)
        buttonframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        button1 = ttk.Button(buttonframe, text="Run Experiment", command=lambda: run())
        button1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button2 = ttk.Button(buttonframe, text="Help", command=lambda: controller.show_frame(HelpPage))
        button2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        def run():
            res.fill(algo())
            print(res.avg_weight)
            print(len(res.avg_weight))
            print(res.fit_graph)
            print(len(res.fit_graph))
            print(res.gens)
            print(len(res.gens))
            print(res.yrs) #int
            print(res.dur) #int
            print(res.pars)
            print(len(res.pars))
            print(res.popfit) #int

            dur.set(res.dur)
            gens.set(len(res.gens))
            yrs.set(res.yrs)
            avgwt.set(res.avg_weight)
            wgtcalc = 0
            for i in res.pars:
                wgtcalc += i
            pars.set(wgtcalc / len(res.pars))
            popfit.set(res.popfit)



class HelpPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Help", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Back to Experiment", command=lambda: controller.show_frame(ExperimentPage))
        button1.pack()


def animate(i):
    a1.clear()
    a1.plot(res.gens, res.fit_graph)
    a2.clear()
    a2.plot(res.gens, res.avg_weight)
    return


# ensure even-number of rats for breeding pairs:
if NUM_RATS % 2 != 0:
    NUM_RATS += 1


def populate(num_rats, min_wt, max_wt, mode_wt):
    """Initialize a population with a triangular distribution of weights."""
    return [int(rn.triangular(min_wt, max_wt, mode_wt))
            for i in range(num_rats)]


def fitness(population, goal):
    """Measure population fitness based on an attribute mean vs target."""
    ave = stat.mean(population)
    return ave / goal


def select(population, to_retain):
    """Cull a population to retain only a specified number of members."""
    sorted_population = sorted(population)
    to_retain_by_sex = to_retain//2
    members_per_sex = len(sorted_population)//2
    females = sorted_population[:members_per_sex]
    males = sorted_population[members_per_sex:]
    selected_females = females[-to_retain_by_sex:]
    selected_males = males[-to_retain_by_sex:]
    return selected_males, selected_females


def breed(males, females, litter_size):
    """Crossover genes among members (weights) of a population."""
    rn.shuffle(males)
    rn.shuffle(females)
    children = []
    for male, female in zip(males, females):
        for child in range(litter_size):
            child = rn.randint(female, male)
            children.append(child)
    return children


def mutate(children, mutate_odds, mutate_min, mutate_max):
    """Randomly alter rat weights using input odds and fractional changes."""
    for index, rat in enumerate(children):
        if mutate_odds >= rn.random():
            children[index] = round(rat * rn.uniform(mutate_min, mutate_max))
    return children


def algo():
    """Initialize population, select, breed, and mutate, then display results."""
    start_time = time.time()
    generations = 0
    parents = populate(NUM_RATS, INITIAL_MIN_WT, INITIAL_MAX_WT, INITIAL_MODE_WT)
    print("Initial population weights = {}".format(parents))
    popl_fitness = fitness(parents, GOAL)
    print("Initial population fitness = {}".format(popl_fitness))
    print("Number to retain = {}".format(NUM_RATS))

    ave_wt = []
    fitness_graph = []

    while popl_fitness < 1 and generations < GENERATION_LIMIT:
        selected_males, selected_females = select(parents, NUM_RATS)
        children = breed(selected_males, selected_females, LITTER_SIZE)
        children = mutate(children, MUTATE_ODDS, MUTATE_MIN, MUTATE_MAX)
        parents = selected_males + selected_females + children
        popl_fitness = fitness(parents, GOAL)
        fitness_graph.append(popl_fitness)
        #print("Generation {} fitness = {:.4f}".format(generations, popl_fitness))
        ave_wt.append(int(stat.mean(parents)))
        generations += 1

    end_time = time.time()
    duration = end_time - start_time
    numyears = generations / LITTERS_PER_YEAR

    #print("\nRuntime for this epoch was {} seconds.".format(duration))
    #print("Average weight per generation = {}".format(ave_wt))
    #print("\nNumber of generations = {}".format(generations))
    #print("Number of years = {}".format(numyears))

    gen_index = []

    for i in range(generations):
        gen_index.append(i)

    return ave_wt, fitness_graph, gen_index, numyears, duration, parents, popl_fitness


def main():
    app = Application()
    ani1 = animation.FuncAnimation(f1, animate, interval=1000)
    ani2 = animation.FuncAnimation(f2, animate, interval=1000)
    app.mainloop()


if __name__ == '__main__':
    main()
