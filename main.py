import time
import statistics as stat
import random as rn
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib import pyplot as plt
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
GENERATION_LIMIT = 5000

# Global Scope configurations
style.use('ggplot')

# ensure even-number of rats for breeding pairs:
if NUM_RATS % 2 != 0:
    NUM_RATS += 1

f = Figure(figsize=(8, 5), dpi=100)
a = f.add_subplot(111)


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


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="favicon.ico")
        tk.Tk.wm_title(self, "Genetic Algorithm v0.1 -- written by Alex F")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Results:
    def __init__(self):
        self.avg_weight = []
        self.fit_graph = []
        self.gens = []
        self.lpy = None
        self.dur = None

    def returnedData(self, output):
        self.avg_weight = output[0]
        self.fit_graph = output[1]
        self.gens = output[2]
        self.lpy = output[3]
        self.dur = output[4]

    def getLPY(self):
        return self.lpy


returnedData = Results()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label1 = ttk.Label(self, text="Genetic Algorithm GUI v0.1", font=LARGE_FONT)
        label1.pack(pady=10, padx=10)

        label2 = ttk.Label(self, text=
                           "An exercise in integrating TKinter, TTK and Matplotlib for a more elegant perspective.",
                           font=SMALL_FONT)
        label2.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        statisticsframe = ttk.LabelFrame(self, text="Statistics")
        statisticsframe.pack(side="right")

        durationframe = ttk.LabelFrame(statisticsframe, text="Duration of Test: ")
        durationframe.pack(side="top", fill="both",  expand=True)

        durationlabel = ttk.Label(durationframe, text="Placeholder for Duration Output")
        durationlabel.pack()

        generationsframe = ttk.LabelFrame(statisticsframe, text="Number of Generations: ")
        generationsframe.pack(side="top", fill="both",  expand=True)

        generationslabel = ttk.Label(generationsframe, text="Placeholder for # Generations")
        generationslabel.pack()

        LPYframe = ttk.LabelFrame(statisticsframe, text="Litters each Year: ")
        LPYframe.pack(side="top", fill="both", expand=True)

        LPYlabel = ttk.Label(LPYframe, text="Placeholder for Litters per Year")
        LPYlabel.pack()

        buttonframe = tk.Frame(self)
        buttonframe.pack(side="left", fill="both", expand=True)

        button1 = ttk.Button(buttonframe, text="Run Experiment", command=lambda: Results.returnedData(self,algo()))
        button1.pack(side="top", fill="both", expand=True)

        button2 = ttk.Button(buttonframe, text="Visit Page 1", command=lambda: a.plot(returnedData.gens, returnedData.fit_graph))
        button2.pack(side="top", fill="both", expand=True)

        button3 = ttk.Button(buttonframe, text="Visit Page 2", command=lambda: controller.show_frame(PageTwo))
        button3.pack(side="top", fill="both", expand=True)


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()


def animate(i):
    # a.clear()
    a.plot(returnedData.gens, returnedData.fit_graph)
    return


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
        print("Generation {} fitness = {:.4f}".format(generations, popl_fitness))
        ave_wt.append(int(stat.mean(parents)))
        generations += 1

    end_time = time.time()
    duration = end_time - start_time

    print("\nRuntime for this epoch was {} seconds.".format(duration))
    print("Average weight per generation = {}".format(ave_wt))
    print("\nNumber of generations = {}".format(generations))
    print("Number of years = {}".format(int(generations / LITTERS_PER_YEAR)))

    gen_index = []

    for i in range(generations):
        gen_index.append(i)
    plt.plot(gen_index, fitness_graph)
    plt.show()

    print(returnedData.getLPY ())

    return ave_wt, fitness_graph, gen_index, LITTERS_PER_YEAR, duration


def main():
    app = Application()
    ani = animation.FuncAnimation(f, animate, interval=5000)
    app.mainloop()


if __name__ == '__main__':
    main()
