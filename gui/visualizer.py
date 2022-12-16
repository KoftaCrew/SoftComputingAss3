import tkinter as tk
from tkinter import ttk
from data.fuzzy_set import FuzzySet
from data.variable import Variable

# Fuzzy sets visualizer


class Visualizer(tk.Canvas):
    variable: Variable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = None
        self.bind("<Configure>", self.draw)

    def draw(self, event=None):
        self.delete("all")
        self.drawVariable()

    def drawVariable(self):
        if self.variable is None:
            return

        w = self.winfo_width()
        h = self.winfo_height()

        # Draw variable name
        self.create_text(
            w / 2,
            0,
            anchor="n",
            text=self.variable.name,
            justify=tk.CENTER,
            font=("Arial", 12, "bold"),
        )

        self.create_polygon(
            0,
            20,
            w - 1,
            20,
            w - 1,
            h - 20,
            0,
            h - 20,
            fill="#ffffff",
            outline="#000000",
        )

        # Draw variable limits
        self.create_line(0, h - 20, 0, h - 13, fill="#000000")

        self.create_text(
            0,
            h - 15,
            text=self.variable.limits[0],
            anchor="nw",
            font=("Arial", 10),
        )

        self.create_line(w - 1, h - 20, w - 1, h - 13, fill="#000000")

        self.create_text(
            w - 1,
            h - 15,
            text=self.variable.limits[1],
            anchor="ne",
            font=("Arial", 10),
        )

        # Draw fuzzy sets
        for i, fuzzySet in enumerate(self.variable.fuzzySets):
            self.drawFuzzySet(fuzzySet, i)

    def drawFuzzySet(self, fuzzySet: FuzzySet, index):
        if fuzzySet.type == "TRI":
            self.drawTri(fuzzySet, index)
        elif fuzzySet.type == "TRAP":
            self.drawTrap(fuzzySet, index)

    def getXOfCrisp(self, x):
        w = self.winfo_width()

        return (x - self.variable.limits[0]) / (
            self.variable.limits[1] - self.variable.limits[0]
        ) * (w - 2) + 1

    def getY(self, y):
        h = self.winfo_height()

        return h - 20 - y * (h - 40)

    def getColor(self, index):
        colors = ["#e60049", "#0bb4ff", "#50e991", "#e6d800",
                  "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff", "#00bfa0"]

        return colors[index % len(colors)]

    def drawTri(self, fuzzySet: FuzzySet, index):
        h = self.winfo_height()

        x1 = self.getXOfCrisp(fuzzySet.values[0])
        x2 = self.getXOfCrisp(fuzzySet.values[1])
        x3 = self.getXOfCrisp(fuzzySet.values[2])

        y1 = self.getY(0)
        y2 = self.getY(1)

        color = self.getColor(index)

        self.create_line(x1, y1, x2, y2, fill=color, width=2)
        self.create_line(x2, y2, x3, y1, fill=color, width=2)

        for i, x in enumerate([x1, x2, x3]):
            if fuzzySet.values[i] not in self.variable.limits:
                self.create_line(x, h - 20, x, h - 13, fill="#000000")
                self.create_text(
                    x,
                    h - 15,
                    text=fuzzySet.values[i],
                    anchor="n",
                    font=("Arial", 10),
                )

        self.create_text(
            x1 + (x3 - x1) / 2,
            self.getY(0.5),
            text=fuzzySet.name,
            anchor="n",
            font=("Arial", 10),
            fill=color,
        )

    def drawTrap(self, fuzzySet: FuzzySet, index):
        h = self.winfo_height()

        x1 = self.getXOfCrisp(fuzzySet.values[0])
        x2 = self.getXOfCrisp(fuzzySet.values[1])
        x3 = self.getXOfCrisp(fuzzySet.values[2])
        x4 = self.getXOfCrisp(fuzzySet.values[3])

        y1 = self.getY(0)
        y2 = self.getY(1)

        color = self.getColor(index)

        self.create_line(x1, y1, x2, y2, fill=color, width=2)
        self.create_line(x2, y2, x3, y2, fill=color, width=2)
        self.create_line(x3, y2, x4, y1, fill=color, width=2)

        for i, x in enumerate([x1, x2, x3, x4]):
            if fuzzySet.values[i] not in self.variable.limits:
                self.create_line(x, h - 20, x, h - 13, fill="#000000")
                self.create_text(
                    x,
                    h - 15,
                    text=fuzzySet.values[i],
                    anchor="n",
                    font=("Arial", 10),
                )

        self.create_text(
            x2 + (x3 - x2) / 2,
            self.getY(0.5),
            text=fuzzySet.name,
            anchor="n",
            font=("Arial", 10),
            fill=color,
        )
