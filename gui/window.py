import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from typing import Literal
import json

from data.variable import *
from data.fuzzy_set import *
from gui.visualizer import Visualizer


class Window:
    _variables: list[Variable]

    def __init__(self):
        self._window = tk.Tk()
        self._window.state('zoomed')
        self._window.minsize(950, 900)

        self.initializeWindow()
        self.newFile()

        self._window.mainloop()

    def initializeWindow(self):
        self._window.columnconfigure(0, weight=3, minsize=400)
        self._window.columnconfigure(1, weight=2, minsize=400)
        self._window.columnconfigure(2, weight=1, minsize=150)

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

        self.selectVariable(None)
        self.selectFuzzySet(None, -1)

    def openFile(self):
        filename = filedialog.askopenfilename(
            title="Open file",
            filetypes=[("JSON files", "*.json")],
        )

        if filename:
            with open(filename, "r") as file:
                data = json.load(file)

                self._variables = []
                for variableData in data["variables"]:
                    variable = Variable(name=variableData["name"], limits=tuple(variableData["limits"]), type=variableData["type"])
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
        }
        if not filename.endswith(".json"):
            filename += ".json"

        with open(filename, "w") as file:
            json.dump(data, file)

        self.filename = filename
        self._window.title(f"Fuzzy logic toolbox - {self.filename}")

    def initializeSimulationFrame(self):
        actionsFrame = ttk.LabelFrame(self._window, text="Simulation")
        actionsFrame.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

        runButton = ttk.Button(actionsFrame, text="Run simulation")
        runButton.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    def initializeVariablesFrame(self):
        variablesFrame = ttk.LabelFrame(self._window, text="Variables")
        variablesFrame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

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

        # Selected variable frame

        self._selectedVariableFrame = ttk.LabelFrame(
            variablesFrame, text="Selected variable")
        self._selectedVariableFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                         expand=True, padx=5, pady=5)

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

        self._rulesEditor = tk.Text(rulesFrame)
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

    def getVariables(self) -> tuple[Variable]:
        return tuple(self._variables)

    def getRules(self) -> str:
        return self._rulesEditor.get("1.0", tk.END)

    def addNewVariable(self, event, variable = None):
        if variable is None:
            variable = Variable(
                name=f"Variable {len(self._variables)}", type=IN, limits=(0, 100),)
            self._variables.append(variable)
        self._variablesList.insert(
            tk.END, f"{variable.name} - {variable.type} - {variable.limits}")

    def removeSelectedVariable(self, event):
        selection = self._variablesList.curselection()
        if selection:
            index = selection[0]
            self._variables.pop(index)
            self._variablesList.delete(index)
            self._variablesList.selection_clear(0, tk.END)
            self.selectVariable(None)

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
