import tkinter as tk
import tkinter.ttk as ttk

from data.variable import Variable


class Window:
    def __init__(self):
        self._window = tk.Tk()
        self._window.title("Fuzzy logic toolbox")
        self._window.state('zoomed')
        self._window.minsize(850, 600)

        self._variables = []

        self.initializeWindow()
        self.populateWindow()

        self._window.mainloop()

    def initializeWindow(self):
        self._window.columnconfigure(0, weight=3, minsize=400)
        self._window.columnconfigure(1, weight=2, minsize=300)
        self._window.columnconfigure(2, weight=1, minsize=150)

        self._window.rowconfigure(0, weight=1)

        rulesFrame = ttk.LabelFrame(self._window, text="Rules")
        rulesFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self._rulesEditor = tk.Text(rulesFrame)
        self._rulesEditor.pack(side=tk.TOP, fill=tk.BOTH,
                               expand=True, padx=5, pady=5)

        variablesFrame = ttk.LabelFrame(self._window, text="Variables")
        variablesFrame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        variableActionsFrame = ttk.Frame(variablesFrame)
        variableActionsFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        variableAddButton = ttk.Button(variableActionsFrame, text="+", width=3)
        variableAddButton.pack(side=tk.LEFT, padx=2)

        variableRemoveButton = ttk.Button(
            variableActionsFrame, text="-", width=3)
        variableRemoveButton.pack(side=tk.LEFT, padx=2)

        self._variablesList = tk.Listbox(variablesFrame)
        self._variablesList.pack(side=tk.TOP, fill=tk.BOTH,
                                 expand=True, padx=5, pady=5)

        selectedVariableFrame = ttk.LabelFrame(
            variablesFrame, text="Selected variable")
        selectedVariableFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                   expand=True, padx=5, pady=5)

        actionsFrame = ttk.LabelFrame(self._window, text="Simulation")
        actionsFrame.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

        runButton = ttk.Button(actionsFrame, text="Run simulation")
        runButton.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    def populateWindow(self):
        for i in range(10):
            self._variablesList.insert(tk.END, f"Variable {i}")

    def getVariables(self) -> tuple[Variable]:
        return tuple(self._variables)

    def getRules(self) -> str:
        return self._rulesEditor.get("1.0", tk.END)
