import re
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import filedialog
from typing import Literal
import json

from data.variable import *
from data.fuzzy_set import *
from engine.engine import simulate
from gui.visualizer import Visualizer


class Window:
    _variables: list[Variable]
    _crispInputs: list[tk.Entry]
    _crispOutputs: list[tk.Label]

    def __init__(self):
        self._window = tk.Tk()
        self._window.state('zoomed')
        self._window.minsize(1050, 700)

        self._variables = []
        self._crispInputs = []
        self._crispOutputs = []

        self.initializeWindow()
        self.newFile()

        self._window.mainloop()

    def initializeWindow(self):
        self._window.columnconfigure(0, weight=3, minsize=400)
        self._window.columnconfigure(1, weight=2, minsize=400)
        self._window.columnconfigure(2, weight=1, minsize=200)

        self._window.rowconfigure(0, weight=1)

        self.initializeRulesFrame()
        self.initializeVariablesFrame()
        self.initializeSimulationFrame()
        self.initializeMenu()

    def initializeMenu(self):
        menu = tk.Menu(self._window)

        fileMenu = tk.Menu(menu, tearoff=0)
        fileMenu.add_command(label="New", command=self.newFile)
        fileMenu.add_command(label="Open", command=self.openFile)
        fileMenu.add_command(label="Save", command=self.saveFile)
        fileMenu.add_command(label="Save as...", command=self.saveFileAs)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self._window.quit)
        menu.add_cascade(label="File", menu=fileMenu)

        self._window.config(menu=menu)

    def newFile(self):
        self.filename = "Untitled"
        self._window.title(f"Fuzzy logic toolbox - {self.filename}")
        self._variables = []
        self._selectedFuzzySetIndex = -1

        self._variablesList.delete(0, tk.END)
        self._variablesList.selection_clear(0, tk.END)
        self._selectedVariableFuzzySetsList.delete(0, tk.END)
        self._selectedVariableFuzzySetsList.selection_clear(0, tk.END)
        self._visualizer.variable = None
        self._visualizer.draw()

        self._rulesEditor.delete("1.0", tk.END)
        self._rulesEditor.insert("1.0", "# Enter the rules in this format:\n" +
                                        "# IN_variable set operator IN_variable set => OUT_variable set\n\n" +
                                        "# Comments start with #\n")

        self._projectTitleEntry.delete(0, tk.END)
        self._projectDescriptionText.delete("1.0", tk.END)

        self.selectVariable(None)
        self.selectFuzzySet(None, -1)
        self.updateVariableFrame()

    def openFile(self):
        filename = filedialog.askopenfilename(
            title="Open file",
            filetypes=[("JSON files", "*.json")],
        )

        if filename:
            with open(filename, "r") as file:
                data = json.load(file)

                self._projectTitleEntry.delete(0, tk.END)
                self._projectTitleEntry.insert(0, data["title"])

                self._projectDescriptionText.delete("1.0", tk.END)
                self._projectDescriptionText.insert("1.0", data["description"])

                self._variables = []
                for variableData in data["variables"]:
                    variable = Variable(name=variableData["name"], limits=tuple(
                        variableData["limits"]), type=variableData["type"])
                    for fuzzySetData in variableData["fuzzySets"]:
                        variable.addFuzzySet(
                            FuzzySet(
                                type=fuzzySetData["type"],
                                values=fuzzySetData["values"],
                                name=fuzzySetData["name"],
                            )
                        )
                    self._variables.append(variable)

                self._rulesEditor.delete("1.0", tk.END)
                self._rulesEditor.insert("1.0", data["rules"])

                self._variablesList.delete(0, tk.END)
                for variable in self._variables:
                    self.addNewVariable(None, variable)

                self._variablesList.selection_clear(0, tk.END)
                self.selectVariable(None)

                for i, entry in enumerate(self._crispInputs):
                    entry.insert(0, data["inputs"][i])

                for i, label in enumerate(self._crispOutputs):
                    label.config(text=data["outputs"][i])

                self.filename = filename
                self._window.title(f"Fuzzy logic toolbox - {self.filename}")

    def saveFile(self):
        if self.filename == "Untitled":
            self.saveFileAs()
        else:
            self.saveToFile(self.filename)

    def saveFileAs(self):
        filename = filedialog.asksaveasfilename(
            title="Save file",
            filetypes=[("JSON files", "*.json")],
            defaultextension="*.*",
        )

        if filename:
            self.saveToFile(filename)

    def saveToFile(self, filename):
        data = {
            "title": self._projectTitleEntry.get(),
            "description": self._projectDescriptionText.get("1.0", tk.END),
            "variables": [
                {
                    "name": variable.name,
                    "limits": variable.limits,
                    "type": variable.type,
                    "fuzzySets": [
                        {
                            "name": fuzzySet.name,
                            "type": fuzzySet.type,
                            "values": fuzzySet.values,
                        }
                        for fuzzySet in variable.fuzzySets
                    ],
                }
                for variable in self._variables
            ],
            "rules": self._rulesEditor.get("1.0", tk.END),
            "inputs": [x.get() for x in self._crispInputs],
            "outputs": [x.cget('text') for x in self._crispOutputs],
        }
        if not filename.endswith(".json"):
            filename += ".json"

        with open(filename, "w") as file:
            json.dump(data, file)

        self.filename = filename
        self._window.title(f"Fuzzy logic toolbox - {self.filename}")

    def initializeSimulationFrame(self):
        simulationFrame = ttk.Frame(self._window)
        simulationFrame.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

        projectDetailsFrame = ttk.LabelFrame(
            simulationFrame, text="Project details")
        projectDetailsFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        projectTitleLabelFrame = ttk.LabelFrame(
            projectDetailsFrame, text="Project title")
        projectTitleLabelFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self._projectTitleEntry = ttk.Entry(projectTitleLabelFrame)
        self._projectTitleEntry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        projectDescriptionLabelFrame = ttk.LabelFrame(
            projectDetailsFrame, text="Project description")
        projectDescriptionLabelFrame.pack(side=tk.TOP, fill=tk.X,
                                          padx=5, pady=5)

        self._projectDescriptionText = tk.Text(
            projectDescriptionLabelFrame, wrap=tk.WORD)
        self._projectDescriptionText.config(height=5, width=30)
        self._projectDescriptionText.pack(side=tk.TOP, fill=tk.X,
                                          padx=5, pady=5)

        variablesFrame = ttk.LabelFrame(simulationFrame, text="Variables")
        variablesFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        variableActionsFrame = ttk.Frame(variablesFrame)
        variableActionsFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        variableAddButton = ttk.Button(variableActionsFrame, text="+", width=3)
        variableAddButton.pack(side=tk.LEFT, padx=2)
        variableAddButton.bind("<Button-1>", self.addNewVariable)

        variableRemoveButton = ttk.Button(
            variableActionsFrame, text="-", width=3)
        variableRemoveButton.pack(side=tk.LEFT, padx=2)
        variableRemoveButton.bind("<Button-1>", self.removeSelectedVariable)

        self._variablesList = tk.Listbox(
            variablesFrame, selectmode=tk.SINGLE, exportselection=False)
        self._variablesList.pack(side=tk.TOP, fill=tk.BOTH,
                                 expand=True, padx=5, pady=5)
        self._variablesList.bind("<<ListboxSelect>>", self.selectVariable)

        actionsFrame = ttk.LabelFrame(simulationFrame, text="Simulation")
        actionsFrame.pack(side=tk.TOP, fill=tk.BOTH,
                          expand=True, padx=5, pady=5)

        
        runButton = ttk.Button(actionsFrame, text="Run simulation")
        runButton.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        runButton.bind("<Button-1>", self.runSimulation)

        # Scrollable frame of variables
        variablesFrame = ttk.Frame(actionsFrame)
        variablesFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        variablesFrameScrollbar = ttk.Scrollbar(
            variablesFrame, orient=tk.VERTICAL)
        variablesFrameScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._variablesCanvas = tk.Canvas(variablesFrame)
        self._variablesCanvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        variablesFrameScrollbar.config(command=self._variablesCanvas.yview)
        self._variablesCanvas.config(
            yscrollcommand=variablesFrameScrollbar.set)

        variablesFrame.bind("<Configure>", lambda e: self._variablesCanvas.configure(
            scrollregion=self._variablesCanvas.bbox("all")))

        self._variablesFrame = ttk.Frame(self._variablesCanvas)
        self._variablesCanvas.create_window((0, 0), window=self._variablesFrame,
                                            anchor=tk.NW)

        self.updateVariableFrame()

    def initializeVariablesFrame(self):
        # Selected variable frame

        self._selectedVariableFrame = ttk.LabelFrame(
            self._window, text="Selected variable")
        self._selectedVariableFrame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableDataFrame = ttk.Frame(self._selectedVariableFrame)
        selectedVariableDataFrame.pack(side=tk.TOP, fill=tk.X)

        selectedVariableDataFrame.columnconfigure(0, weight=1, minsize=50)
        selectedVariableDataFrame.columnconfigure(1, weight=3)

        selectedVariableDataNameLabel = ttk.Label(
            selectedVariableDataFrame, text="Name:")
        selectedVariableDataNameLabel.grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self._selectedVariableNameEntry = ttk.Entry(
            selectedVariableDataFrame)
        self._selectedVariableNameEntry.grid(
            row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableTypeLabel = ttk.Label(
            selectedVariableDataFrame, text="Type:")
        selectedVariableTypeLabel.grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self._selectedVariableTypeCombobox = ttk.Combobox(
            selectedVariableDataFrame, state="readonly", values=["IN", "OUT"])
        self._selectedVariableTypeCombobox.grid(
            row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableRangeLabel = ttk.Label(
            selectedVariableDataFrame, text="Range:")
        selectedVariableRangeLabel.grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableRangeFrame = ttk.Frame(selectedVariableDataFrame)
        selectedVariableRangeFrame.grid(
            row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self._selectedVariableRangeFromEntry = ttk.Entry(
            selectedVariableRangeFrame)
        self._selectedVariableRangeFromEntry.config(width=5)
        self._selectedVariableRangeFromEntry.pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        selectedVariableRangeSeparatorLabel = ttk.Label(
            selectedVariableRangeFrame, text=" - ")
        selectedVariableRangeSeparatorLabel.pack(side=tk.LEFT, padx=5)

        self._selectedVariableRangeToEntry = ttk.Entry(
            selectedVariableRangeFrame)
        self._selectedVariableRangeToEntry.config(width=5)
        self._selectedVariableRangeToEntry.pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        selectedVariableFuzzySetsFrame = ttk.LabelFrame(
            self._selectedVariableFrame, text="Fuzzy sets")
        selectedVariableFuzzySetsFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                            expand=True, padx=5, pady=5)

        selectedVariableFuzzySetsActionsFrame = ttk.Frame(
            selectedVariableFuzzySetsFrame)
        selectedVariableFuzzySetsActionsFrame.pack(side=tk.TOP, fill=tk.X,
                                                   padx=5, pady=5)

        self._selectedVariableFuzzySetsAddButton = ttk.Button(
            selectedVariableFuzzySetsActionsFrame, text="+", width=3)
        self._selectedVariableFuzzySetsAddButton.pack(side=tk.LEFT, padx=2)

        self._selectedVariableFuzzySetsRemoveButton = ttk.Button(
            selectedVariableFuzzySetsActionsFrame, text="-", width=3)
        self._selectedVariableFuzzySetsRemoveButton.pack(side=tk.LEFT, padx=2)

        self._selectedVariableFuzzySetsList = tk.Listbox(
            selectedVariableFuzzySetsFrame, selectmode=tk.SINGLE, exportselection=False)
        self._selectedVariableFuzzySetsList.pack(side=tk.TOP, fill=tk.BOTH,
                                                 expand=True, padx=5, pady=5)

        self._selectedVariableFuzzySetDataFrame = ttk.Frame(
            selectedVariableFuzzySetsFrame)
        self._selectedVariableFuzzySetDataFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                                     expand=True, padx=5, pady=5)

        self._selectedVariableFuzzySetDataFrame.columnconfigure(
            0, weight=1, minsize=50)
        self._selectedVariableFuzzySetDataFrame.columnconfigure(1, weight=3)

        selectedVariableFuzzySetDataNameLabel = ttk.Label(
            self._selectedVariableFuzzySetDataFrame, text="Name:")
        selectedVariableFuzzySetDataNameLabel.grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self._selectedVariableFuzzySetNameEntry = ttk.Entry(
            self._selectedVariableFuzzySetDataFrame)
        self._selectedVariableFuzzySetNameEntry.grid(
            row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableFuzzySetTypeLabel = ttk.Label(
            self._selectedVariableFuzzySetDataFrame, text="Type:")
        selectedVariableFuzzySetTypeLabel.grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self._selectedVariableFuzzySetTypeCombobox = ttk.Combobox(
            self._selectedVariableFuzzySetDataFrame, state="readonly", values=["Triangle", "Trapezoid"])
        self._selectedVariableFuzzySetTypeCombobox.grid(
            row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableFuzzySetRangeLabel = ttk.Label(
            self._selectedVariableFuzzySetDataFrame, text="Range:")
        selectedVariableFuzzySetRangeLabel.grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableFuzzySetPointsFrame = ttk.Frame(
            self._selectedVariableFuzzySetDataFrame)
        selectedVariableFuzzySetPointsFrame.grid(
            row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self._selectedVariableFuzzySetPointsEntry = [
            ttk.Entry(selectedVariableFuzzySetPointsFrame) for _ in range(4)]
        for i, entry in enumerate(self._selectedVariableFuzzySetPointsEntry):
            entry.config(width=5)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if i != 3:
                ttk.Label(selectedVariableFuzzySetPointsFrame,
                          text=" - ").pack(side=tk.LEFT, padx=5)

        # Disable all widgets in selectedVariableFrame if no variable is selected
        self.setFrameState(self._selectedVariableFrame, tk.DISABLED)

        visualizerLabelFrame = ttk.LabelFrame(
            self._selectedVariableFrame, text="Visualizer")
        visualizerLabelFrame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        visualizerFrame = tk.Frame(visualizerLabelFrame)
        visualizerFrame.config(background="white")
        visualizerFrame.pack(side=tk.TOP, fill=tk.BOTH,
                             expand=True, padx=5, pady=5)

        self._visualizer = Visualizer(
            visualizerFrame, background="white", highlightthickness=0)
        self._visualizer.pack(side=tk.TOP, fill=tk.BOTH,
                              expand=True, padx=5, pady=5)

    def initializeRulesFrame(self):
        rulesFrame = ttk.LabelFrame(self._window, text="Rules")
        rulesFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self._rulesEditor = tk.Text(rulesFrame, wrap=tk.WORD)
        self._rulesEditor.pack(side=tk.TOP, fill=tk.BOTH,
                               expand=True, padx=5, pady=5)

    def setFrameState(self, frame: tk.Widget, state: Literal["normal", "disabled"]):
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame) or isinstance(child, ttk.Frame):
                self.setFrameState(child, state)
            elif isinstance(child, ttk.Labelframe):
                self.setFrameState(child, state)
                if state == tk.DISABLED:
                    child.state([tk.DISABLED])
                else:
                    child.state(["!disabled"])
            else:
                child.configure(state=state)

    def getRules(self) -> str:
        return self._rulesEditor.get("1.0", tk.END)

    def addNewVariable(self, event, variable=None):
        if variable is None:
            variable = Variable(
                name=f"Variable {len(self._variables)}", type=IN, limits=(0, 100),)
            self._variables.append(variable)
        self._variablesList.insert(
            tk.END, f"{variable.name} - {variable.type} - {variable.limits}")
        self.updateVariableFrame()

    def removeSelectedVariable(self, event):
        selection = self._variablesList.curselection()
        if selection:
            index = selection[0]
            self._variables.pop(index)
            self._variablesList.delete(index)
            self._variablesList.selection_clear(0, tk.END)
            self.selectVariable(None)
        self.updateVariableFrame()

    def selectVariable(self, event):
        selection = self._variablesList.curselection()
        if selection:
            index = selection[0]
            self.setFrameState(self._selectedVariableFrame, tk.NORMAL)
            self._selectedVariableNameEntry.delete(0, tk.END)
            self._selectedVariableNameEntry.insert(
                0, self._variables[index].name)
            self._selectedVariableTypeCombobox.set(self._variables[index].type)
            self._selectedVariableTypeCombobox.state(["readonly"])
            self._selectedVariableRangeFromEntry.delete(0, tk.END)
            self._selectedVariableRangeFromEntry.insert(
                0, self._variables[index].limits[0])
            self._selectedVariableRangeToEntry.delete(0, tk.END)
            self._selectedVariableRangeToEntry.insert(
                0, self._variables[index].limits[1])

            self._selectedVariableFuzzySetsList.delete(0, tk.END)
            for fuzzySet in self._variables[index].fuzzySets:
                self._selectedVariableFuzzySetsList.insert(
                    tk.END, fuzzySet.name)
            self._selectedVariableFuzzySetsList.config(
                selectmode=tk.SINGLE, exportselection=False)
            self._selectedVariableFuzzySetsList.selection_set(-1)
            self._selectedFuzzySetIndex = -1

            self._visualizer.variable = self._variables[index]
            self._visualizer.draw()

            self.setFrameState(
                self._selectedVariableFuzzySetDataFrame, tk.DISABLED)

            # Add listeners
            self._selectedVariableNameEntry.bind(
                "<KeyRelease>", lambda event: self.updateVariableUi(event, index))
            self._selectedVariableTypeCombobox.bind(
                "<<ComboboxSelected>>", lambda event: self.updateVariableUi(event, index))
            self._selectedVariableRangeFromEntry.bind(
                "<KeyRelease>", lambda event: self.updateVariableUi(event, index))
            self._selectedVariableRangeToEntry.bind(
                "<KeyRelease>", lambda event: self.updateVariableUi(event, index))
            self._selectedVariableFuzzySetsList.bind(
                "<<ListboxSelect>>", lambda event: self.selectFuzzySet(event, index))
            self._selectedVariableFuzzySetsAddButton.bind(
                "<Button-1>", lambda event: self.addNewFuzzySet(event, index))
            self._selectedVariableFuzzySetsRemoveButton.bind(
                "<Button-1>", lambda event: self.removeSelectedFuzzySet(event, index))
        else:
            self.setFrameState(self._selectedVariableFrame, tk.DISABLED)

            # Remove listeners
            self._selectedVariableNameEntry.unbind("<KeyRelease>")
            self._selectedVariableTypeCombobox.unbind("<<ComboboxSelected>>")
            self._selectedVariableRangeFromEntry.unbind("<KeyRelease>")
            self._selectedVariableRangeToEntry.unbind("<KeyRelease>")
            self._selectedVariableFuzzySetsList.unbind("<<ListboxSelect>>")
            self._selectedVariableFuzzySetsAddButton.unbind("<Button-1>")
            self._selectedVariableFuzzySetsRemoveButton.unbind("<Button-1>")

    def updateVariableUi(self, event, index):
        self._variables[index].name = self._selectedVariableNameEntry.get()
        self._variables[index].type = self._selectedVariableTypeCombobox.get()
        fromRange, toRange = self._selectedVariableRangeFromEntry.get(
        ), self._selectedVariableRangeToEntry.get()
        if fromRange.isdigit() and toRange.isdigit() and int(fromRange) < int(toRange):
            self._variables[index].limits = (int(fromRange), int(toRange))
        else:
            self._selectedVariableRangeFromEntry.delete(0, tk.END)
            self._selectedVariableRangeFromEntry.insert(
                0, self._variables[index].limits[0])
            self._selectedVariableRangeToEntry.delete(0, tk.END)
            self._selectedVariableRangeToEntry.insert(
                0, self._variables[index].limits[1])
        self._variablesList.delete(index)
        self._variablesList.insert(
            index, f"{self._variables[index].name} - {self._variables[index].type} - {self._variables[index].limits}")
        self._variablesList.selection_set(index)
        self._visualizer.draw()
        self.updateVariableFrame()

    def addNewFuzzySet(self, event, index):
        fuzzySet = FuzzySet(name=f"Set {len(self._variables[index].fuzzySets)}",
                            values=(0, 0, 0), type=TRI)
        self._variables[index].fuzzySets.append(fuzzySet)
        self._selectedVariableFuzzySetsList.insert(
            tk.END, fuzzySet.name)

    def removeSelectedFuzzySet(self, event, index):
        selection = self._selectedVariableFuzzySetsList.curselection()
        if selection:
            fuzzySetIndex = selection[0]
            self._variables[index].fuzzySets.pop(fuzzySetIndex)
            self._selectedVariableFuzzySetsList.delete(fuzzySetIndex)
            self._selectedVariableFuzzySetsList.selection_set(-1)
            self.selectFuzzySet(None, index)

    def selectFuzzySet(self, event, index):
        selection = self._selectedVariableFuzzySetsList.curselection()
        if selection:
            fuzzySetIndex = selection[0]
            if self._selectedFuzzySetIndex != -1:
                self.updateFuzzySetUi(
                    event, index, self._selectedFuzzySetIndex, select=False)
            self._selectedFuzzySetIndex = fuzzySetIndex

            self.setFrameState(
                self._selectedVariableFuzzySetDataFrame, tk.NORMAL)
            self._selectedVariableFuzzySetNameEntry.delete(0, tk.END)
            self._selectedVariableFuzzySetNameEntry.insert(
                0, self._variables[index].fuzzySets[fuzzySetIndex].name)
            for i, value in enumerate(self._variables[index].fuzzySets[fuzzySetIndex].values):
                self._selectedVariableFuzzySetPointsEntry[i].delete(0, tk.END)
                self._selectedVariableFuzzySetPointsEntry[i].insert(0, value)
            self._selectedVariableFuzzySetTypeCombobox.set(
                self._variables[index].fuzzySets[fuzzySetIndex].type)
            self._selectedVariableFuzzySetTypeCombobox.state(
                ["readonly"])
            self._selectedVariableFuzzySetPointsEntry[3].config(
                state=tk.DISABLED if self._variables[index].fuzzySets[fuzzySetIndex].type == TRI else tk.NORMAL)

            # Add listeners
            self._selectedVariableFuzzySetNameEntry.bind(
                "<KeyRelease>", lambda event: self.updateFuzzySetUi(event, index, fuzzySetIndex))
            for entry in self._selectedVariableFuzzySetPointsEntry:
                entry.bind(
                    "<FocusOut>", lambda event: self.updateFuzzySetUi(event, index, fuzzySetIndex))
            self._selectedVariableFuzzySetTypeCombobox.bind(
                "<<ComboboxSelected>>", lambda event: self.updateFuzzySetUi(event, index, fuzzySetIndex))
        else:
            self._selectedFuzzySetIndex = -1
            self.setFrameState(
                self._selectedVariableFuzzySetDataFrame, tk.DISABLED)

            # Remove listeners
            self._selectedVariableFuzzySetNameEntry.unbind("<KeyRelease>")
            for entry in self._selectedVariableFuzzySetPointsEntry:
                entry.unbind("<KeyRelease>")
            self._selectedVariableFuzzySetTypeCombobox.unbind(
                "<<ComboboxSelected>>")

    def updateFuzzySetUi(self, event, index, fuzzySetIndex, select=True):
        self._variables[index].fuzzySets[fuzzySetIndex].name = self._selectedVariableFuzzySetNameEntry.get()
        if self._selectedVariableFuzzySetTypeCombobox.get() == "Triangle":
            self._variables[index].fuzzySets[fuzzySetIndex].type = TRI
            if len(self._variables[index].fuzzySets[fuzzySetIndex].values) == 4:
                self._variables[index].fuzzySets[fuzzySetIndex].values = tuple(
                    self._variables[index].fuzzySets[fuzzySetIndex].values[:3])
        elif self._selectedVariableFuzzySetTypeCombobox.get() == "Trapezoid":
            self._variables[index].fuzzySets[fuzzySetIndex].type = TRAP
            if len(self._variables[index].fuzzySets[fuzzySetIndex].values) == 3:
                self._variables[index].fuzzySets[fuzzySetIndex].values += (0,)

        if self._variables[index].fuzzySets[fuzzySetIndex].type == TRI:
            self._selectedVariableFuzzySetPointsEntry[3].delete(0, tk.END)
        self._selectedVariableFuzzySetPointsEntry[3].config(
            state=tk.NORMAL if self._variables[index].fuzzySets[fuzzySetIndex].type == TRAP else tk.DISABLED)

        points = [x.get() for x in self._selectedVariableFuzzySetPointsEntry]
        if self._variables[index].fuzzySets[fuzzySetIndex].type == TRI:
            points = points[:3]
        if all([x.isdigit() for x in points]):
            inputPoints = tuple([int(x) for x in points])
            # Change only if sorted
            if sorted(inputPoints) == list(inputPoints):
                self._variables[index].fuzzySets[fuzzySetIndex].values = inputPoints
        else:
            for i, entry in enumerate(self._selectedVariableFuzzySetPointsEntry):
                entry.delete(0, tk.END)
                entry.insert(
                    0, self._variables[index].fuzzySets[fuzzySetIndex].values[i])

        self._selectedVariableFuzzySetsList.delete(fuzzySetIndex)
        self._selectedVariableFuzzySetsList.insert(
            fuzzySetIndex, self._variables[index].fuzzySets[fuzzySetIndex].name)
        if select:
            self._selectedVariableFuzzySetsList.selection_set(fuzzySetIndex)

        self._visualizer.draw()

    def updateVariableFrame(self):
        for widget in self._variablesFrame.winfo_children():
            widget.destroy()
        self._variablesFrame.columnconfigure(0, weight=1)
        self._variablesFrame.columnconfigure(1, weight=1)

        i = 0
        self._crispInputs = []
        for variable in self._variables:
            if variable.type == OUT:
                continue
            variableLabel = ttk.Label(
                self._variablesFrame, text=f"{variable.name}:")
            variableLabel.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            variableEntry = ttk.Entry(self._variablesFrame)
            variableEntry.grid(row=i, column=1, sticky=tk.NSEW, padx=5, pady=5)
            self._crispInputs.append(variableEntry)

            i += 1

        self._crispOutputs = []
        for variable in self._variables:
            if variable.type == IN:
                continue
            variableLabel = ttk.Label(
                self._variablesFrame, text=f"{variable.name}:")
            variableLabel.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            variableEntry = ttk.Label(self._variablesFrame)
            variableEntry.grid(row=i, column=1, sticky=tk.NSEW, padx=5, pady=5)
            self._crispOutputs.append(variableEntry)

            i += 1

        self._variablesCanvas.update()
        self._variablesCanvas.update_idletasks()
        self._variablesCanvas.configure(scrollregion=self._variablesCanvas.bbox("all"))

    def runSimulation(self, event=None):
        rules = self.getRules().strip().split("\n")
        rules = [re.sub(r'#.*', '', x) for x in rules]
        rules = [x.strip() for x in rules]
        rules = [x for x in rules if x != ""]
        if len(rules) == 0:
            messagebox.showerror("Error", "Can't run simulation without rules")
            return

        if len(self._variables) == 0:
            messagebox.showerror("Error", "Can't run simulation, please define variables")
            return

        for variable in self._variables:
            if len(variable.fuzzySets) == 0:
                messagebox.showerror("Error", "Can't run simulation, please define fuzzy sets for all variables")
                return

        crispInputs: list[str] = [x.get() for x in self._crispInputs]
        try:
            crispInputs = [float(x) for x in crispInputs]
        except ValueError:
            messagebox.showerror(
                "Error", "All inputs must be numbers")
            return

        for i, variable in enumerate(filter(lambda x: x.type == IN, self._variables)):
            if crispInputs[i] < variable.limits[0] or crispInputs[i] > variable.limits[1]:
                messagebox.showerror(
                    "Error", f"Input {variable.name} must be between {variable.limits[0]} and {variable.limits[1]}")
                return

        try:
            outputs = simulate(self._variables, crispInputs, rules)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        for i, (output, set) in enumerate(outputs):
            self._crispOutputs[i].config(text=f"{round(output, 2)} ({set})")
