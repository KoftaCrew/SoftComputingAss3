import tkinter as tk
import tkinter.ttk as ttk
from typing import Literal

from data.variable import *


class Window:
    def __init__(self):
        self._window = tk.Tk()
        self._window.title("Fuzzy logic toolbox")
        self._window.state('zoomed')
        self._window.minsize(950, 600)

        self._variables = []

        self.initializeWindow()

        self._window.mainloop()

    def initializeWindow(self):
        self._window.columnconfigure(0, weight=3, minsize=400)
        self._window.columnconfigure(1, weight=2, minsize=400)
        self._window.columnconfigure(2, weight=1, minsize=150)

        self._window.rowconfigure(0, weight=1)

        self.initializeRulesFrame()
        self.initializeVariablesFrame()
        self.initializeSimulationFrame()

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

        self._variablesList = tk.Listbox(variablesFrame)
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

        selectedVariableNameEntry = ttk.Entry(
            selectedVariableDataFrame)
        selectedVariableNameEntry.grid(
            row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableTypeLabel = ttk.Label(
            selectedVariableDataFrame, text="Type:")
        selectedVariableTypeLabel.grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableTypeCombobox = ttk.Combobox(
            selectedVariableDataFrame, state="readonly", values=["IN", "OUT"])
        selectedVariableTypeCombobox.grid(
            row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableRangeLabel = ttk.Label(
            selectedVariableDataFrame, text="Range:")
        selectedVariableRangeLabel.grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableRangeFrame = ttk.Frame(selectedVariableDataFrame)
        selectedVariableRangeFrame.grid(
            row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableRangeFromEntry = ttk.Entry(
            selectedVariableRangeFrame)
        selectedVariableRangeFromEntry.config(width=5)
        selectedVariableRangeFromEntry.pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        selectedVariableRangeSeparatorLabel = ttk.Label(
            selectedVariableRangeFrame, text=" - ")
        selectedVariableRangeSeparatorLabel.pack(side=tk.LEFT, padx=5)

        selectedVariableRangeToEntry = ttk.Entry(
            selectedVariableRangeFrame)
        selectedVariableRangeToEntry.config(width=5)
        selectedVariableRangeToEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        selectedVariableFuzzySetsFrame = ttk.LabelFrame(
            self._selectedVariableFrame, text="Fuzzy sets")
        selectedVariableFuzzySetsFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                            expand=True, padx=5, pady=5)

        selectedVariableFuzzySetsActionsFrame = ttk.Frame(
            selectedVariableFuzzySetsFrame)
        selectedVariableFuzzySetsActionsFrame.pack(side=tk.TOP, fill=tk.X,
                                                   padx=5, pady=5)

        selectedVariableFuzzySetsAddButton = ttk.Button(
            selectedVariableFuzzySetsActionsFrame, text="+", width=3)
        selectedVariableFuzzySetsAddButton.pack(side=tk.LEFT, padx=2)

        selectedVariableFuzzySetsRemoveButton = ttk.Button(
            selectedVariableFuzzySetsActionsFrame, text="-", width=3)
        selectedVariableFuzzySetsRemoveButton.pack(side=tk.LEFT, padx=2)

        selectedVariableFuzzySetsList = tk.Listbox(
            selectedVariableFuzzySetsFrame)
        selectedVariableFuzzySetsList.pack(side=tk.TOP, fill=tk.BOTH,
                                           expand=True, padx=5, pady=5)

        selectedVariableFuzzySetDataFrame = ttk.Frame(
            selectedVariableFuzzySetsFrame)
        selectedVariableFuzzySetDataFrame.pack(side=tk.TOP, fill=tk.BOTH,
                                               expand=True, padx=5, pady=5)

        selectedVariableFuzzySetDataFrame.columnconfigure(
            0, weight=1, minsize=50)
        selectedVariableFuzzySetDataFrame.columnconfigure(1, weight=3)

        selectedVariableFuzzySetDataNameLabel = ttk.Label(
            selectedVariableFuzzySetDataFrame, text="Name:")
        selectedVariableFuzzySetDataNameLabel.grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableFuzzySetNameEntry = ttk.Entry(
            selectedVariableFuzzySetDataFrame)
        selectedVariableFuzzySetNameEntry.grid(
            row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableFuzzySetTypeLabel = ttk.Label(
            selectedVariableFuzzySetDataFrame, text="Type:")
        selectedVariableFuzzySetTypeLabel.grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableFuzzySetTypeCombobox = ttk.Combobox(
            selectedVariableFuzzySetDataFrame, state="readonly", values=["Triangle", "Trapezoid"])
        selectedVariableFuzzySetTypeCombobox.grid(
            row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableFuzzySetRangeLabel = ttk.Label(
            selectedVariableFuzzySetDataFrame, text="Range:")
        selectedVariableFuzzySetRangeLabel.grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        selectedVariableFuzzySetPointsFrame = ttk.Frame(
            selectedVariableFuzzySetDataFrame)
        selectedVariableFuzzySetPointsFrame.grid(
            row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)

        selectedVariableFuzzySetPointsEntry = [
            ttk.Entry(selectedVariableFuzzySetPointsFrame) for _ in range(4)]
        for i, entry in enumerate(selectedVariableFuzzySetPointsEntry):
            entry.config(width=5)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if i != 3:
                ttk.Label(selectedVariableFuzzySetPointsFrame,
                          text=" - ").pack(side=tk.LEFT, padx=5)

        # Disable all widgets in selectedVariableFrame if no variable is selected
        self.changeFrameState(self._selectedVariableFrame, tk.DISABLED)

    def initializeRulesFrame(self):
        rulesFrame = ttk.LabelFrame(self._window, text="Rules")
        rulesFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self._rulesEditor = tk.Text(rulesFrame)
        self._rulesEditor.pack(side=tk.TOP, fill=tk.BOTH,
                               expand=True, padx=5, pady=5)

    def changeFrameState(self, frame: tk.Widget, state: Literal["normal", "disabled"]):
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame) or isinstance(child, ttk.Frame):
                self.changeFrameState(child, state)
            elif isinstance(child, ttk.Labelframe):
                self.changeFrameState(child, state)
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

    def addNewVariable(self, event):
        variable = Variable(name=f"Variable {len(self._variables)}", type=IN, limits=(0, 100),)
        self._variables.append(variable)
        self._variablesList.insert(tk.END, f"{variable.name} - {variable.type} - {variable.limits}")

    def removeSelectedVariable(self, event):
        selection = self._variablesList.curselection()
        if selection:
            index = selection[0]
            self._variables.pop(index)
            self._variablesList.delete(index)

    def selectVariable(self, event):
        selection = self._variablesList.curselection()
        if selection:
            index = selection[0]
            self.changeFrameState(self._selectedVariableFrame, tk.NORMAL)
            # self._selectedVariableNameEntry.delete(0, tk.END)
            # self._selectedVariableNameEntry.insert(0, self._variables[index].name)
            # self._selectedVariableTypeCombobox.set(self._variables[index].type)
            # self._selectedVariableLimitsEntry.delete(0, tk.END)
            # self._selectedVariableLimitsEntry.insert(0, self._variables[index].limits)
        else:
            self.changeFrameState(self._selectedVariableFrame, tk.DISABLED)
