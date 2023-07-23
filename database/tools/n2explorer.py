# this file is part of refractiveindex.info database
# refractiveindex.info database is in the public domain
# copyright and related rights waived via CC0 1.0

import sys
import yaml
import os
import re

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QComboBox, QCheckBox, QRadioButton, QSpacerItem, QTextBrowser, QTabWidget
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


# arrays for library structure and content
shelf_ids = []
shelf_names = []
shelf_info_paths = []

book_ids = []
book_names = []
book_info_paths = []

page_ids = []
page_names = []
page_paths = []
page_info_paths = []

wl = []
n2 = []

# we assume that this script is in the "tools" directory of the RII database
current_file_path = os.path.abspath(__file__)
db_path = os.path.dirname(os.path.dirname(current_file_path))

lib_path = os.path.join(db_path, "catalog-n2.yml")
library = yaml.safe_load(open(lib_path, "r", encoding="utf-8").read())

fig, ax = plt.subplots()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Shelves and Books combo boxes
        self.combobox1 = QComboBox()
        self.combobox2 = QComboBox()

        # Plot
        self.canvas = FigureCanvas(fig)

        # Detailed output box
        self.details = QTextBrowser()
        self.details.setOpenExternalLinks(True)

        # Info box
        self.info = QTextBrowser()
        self.info.setOpenExternalLinks(True)

        # Page checkboxes (added/removed later depending on number of pages)
        self.checkboxes = []
        self.checkboxes_layout = QVBoxLayout()
        spacer1 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.checkboxes_layout.addSpacerItem(spacer1)

        # Page checkboxes (added/removed later depending on number of pages)
        self.radiobuttons = []
        self.radiobuttons_layout = QVBoxLayout()
        spacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.radiobuttons_layout.addSpacerItem(spacer2)

        # Tab widget
        tab_widget = QTabWidget()

        # Explorer tab
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.addLayout(self.checkboxes_layout)
        tab1_layout.addWidget(self.canvas)
        tab1_layout.setStretchFactor(self.canvas, 1) # stretch figure
        tab_widget.addTab(tab1, "Data explorer")

        # Details tab
        tab2 = QWidget()
        tab2_layout = QHBoxLayout(tab2)
        tab2_layout.addLayout(self.radiobuttons_layout)
        tab2_layout.addWidget(self.details)
        tab2_layout.setStretchFactor(self.details, 1) # stretch text box
        tab_widget.addTab(tab2, "Details")

        # Info tab
        tab3 = QWidget()
        tab3_layout = QHBoxLayout(tab3)
        tab3_layout.addWidget(self.info)
        tab_widget.addTab(tab3, "Info")

        # populate main_layout (vertical)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.combobox1)
        main_layout.addWidget(self.combobox2)
        main_layout.addWidget(tab_widget)

        window = QWidget()
        window.setWindowTitle("n2 Explorer")
        window.setLayout(main_layout)

        self.combobox1.currentIndexChanged.connect(UpdateBookList)
        self.combobox2.currentIndexChanged.connect(UpdatePageList)

        self.setCentralWidget(window)



def UpdateShelfList():
    global shelf_names, shelf_info_paths
    shelf_ids = []
    shelf_names = []
    shelf_info_paths = []
    for shelf in library:
        if "SHELF" in shelf:
            shelf_ids.append(shelf.get("SHELF"))
            shelf_names.append(shelf.get("name"))
            shelf_info_paths.append(shelf.get("info"))
            w.combobox1.addItem(shelf.get("name"))
        elif "DIVIDER" in shelf:
            shelf_ids.append("")
            shelf_names.append("")
            shelf_info_paths.append("")
            # add disabled item as divider
            w.combobox1.addItem("   " + shelf.get("DIVIDER"))
            w.combobox1.model().item(w.combobox1.count()-1).setEnabled(False)
    # select first enabled item
    for i in range(w.combobox1.count()):
        if w.combobox1.model().item(i).isEnabled():
            w.combobox1.setCurrentIndex(i)
            break

def UpdateBookList():
    global book_ids, book_names, book_info_paths

    shelf = library[w.combobox1.currentIndex()].get("content")
    if not shelf:
        return

    w.combobox2.clear()
    book_ids = []
    book_names = []
    book_info_paths = []
    
    for book in shelf:
        if "BOOK" in book:
            book_ids.append(book.get("BOOK"))
            book_names.append(book.get("name"))
            book_info_paths.append(book.get("info"))
            w.combobox2.addItem(re.sub("<[^<]+?>", "", book.get("name"))) # strip HTML tags from name)
        elif "DIVIDER" in book:
            book_ids.append("")
            book_names.append("")
            book_info_paths.append("")
            # add disabled item as divider
            w.combobox2.addItem("   " + book.get("DIVIDER"))
            w.combobox2.model().item(w.combobox2.count()-1).setEnabled(False)
    # select first enabled item
    for i in range(w.combobox2.count()):
        if w.combobox2.model().item(i).isEnabled():
            w.combobox2.setCurrentIndex(i)
            break

def UpdatePageList():
    global page_ids, page_names, page_paths, page_info_paths

    shelf = library[w.combobox1.currentIndex()].get("content")
    if not shelf:
        return
    book = shelf[w.combobox2.currentIndex()].get("content")
    if not book:
        return

    page_ids = []
    page_names = []
    page_paths = []
    page_info_paths = []
    # remove all checkboxes
    while w.checkboxes:
        checkbox = w.checkboxes.pop()
        checkbox.setParent(None)
        checkbox.deleteLater()
    # remove all radiobuttons
    while w.radiobuttons:
        radiobutton = w.radiobuttons.pop()
        radiobutton.setParent(None)
        radiobutton.deleteLater()
    for i, page in enumerate(book):
        if "PAGE" in page:
            page_ids.append(page.get("PAGE"))
            page_names.append(page.get("name"))
            page_paths.append(page.get("data"))
            page_info_paths.append(page.get("info"))
            # add a checked checkbox
            checkbox = QCheckBox(html2mathtext(page.get("name")))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(UpdatePlot)
            w.checkboxes.append(checkbox)
            w.checkboxes_layout.insertWidget(i, checkbox)
            # add a radiobutton and check the first enabled radiobutton
            radiobutton = QRadioButton(html2mathtext(page.get("name")))
            is_any_radiobutton_checked = False
            for j in range(w.radiobuttons_layout.count()):
                widget = w.radiobuttons_layout.itemAt(j).widget()
                if isinstance(widget, QRadioButton) and widget.isChecked():
                    is_any_radiobutton_checked = True
            radiobutton.setChecked(not is_any_radiobutton_checked)
            radiobutton.toggled.connect(UpdateDetails)
            w.radiobuttons.append(radiobutton)
            w.radiobuttons_layout.insertWidget(i, radiobutton)
        if "DIVIDER" in page:
            page_ids.append("")
            page_names.append("")
            page_paths.append("")
            page_info_paths.append("")
            # add a hidden checkbox (label only)
            checkbox = QCheckBox(html2mathtext(page.get("DIVIDER")))
            checkbox.setEnabled(False)
            checkbox.setStyleSheet("QCheckBox::indicator {width: 0px; height: 0px;}")
            w.checkboxes.append(checkbox)
            w.checkboxes_layout.insertWidget(i, checkbox)
            # add a hidden radiobutton
            radiobutton = QRadioButton(html2mathtext(page.get("DIVIDER")))
            radiobutton.setEnabled(False)
            radiobutton.setStyleSheet("QRadioButton::indicator {width: 0px; height: 0px;}")
            w.radiobuttons.append(radiobutton)
            w.radiobuttons_layout.insertWidget(i, radiobutton)
    UpdateData()
    UpdatePlot()
    UpdateDetails()
    UpdateInfo()


def UpdateData():
    global wl, n2
    wl = []
    n2 = []
    for i in range(len(page_ids)):
        if page_ids[i] == "": # DIVIDER
            wl.append(0)
            n2.append(0)
            continue
        data_path = os.path.join(db_path, "data-n2", page_paths[i])
        data_path = os.path.normpath(data_path)
        if os.path.exists(data_path):
            datafile = yaml.safe_load(open(data_path, "r", encoding="utf-8").read())
            for data in datafile.get("DATA"):
                if (data.get("type").split())[0] == "tabulated":
                    rows = data.get("data").split("\n")
                    splitrows = [c.split() for c in rows]
                    tmp_wl = []
                    tmp_n2 = []
                    for s in splitrows:
                        if len(s) > 0:
                            tmp_wl.append(float(s[0]))
                            tmp_n2.append(float(s[1]))
            wl.append(tmp_wl)
            n2.append(tmp_n2)


def UpdatePlot():
    ax.clear()
    all_n2_positive = True
    for i in range(len(page_ids)):
        if page_ids[i] == "": # DIVIDER
            continue
        if w.checkboxes[i].isChecked():
            ax.scatter(wl[i], n2[i], label=page_ids[i]) # dots
            ax.plot(wl[i], n2[i]) # lines
            for k in range(len(n2[i])):
                if n2[i][k] < 0:
                    all_n2_positive = False
    ax.set_title(html2mathtext(book_names[w.combobox2.currentIndex()]))
    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("n$_2$ (m$^2$/W)")
    if all_n2_positive:
        ax.set_ylim(ymin=0)
    ax.grid()
    ax.legend()
    fig.tight_layout()
    w.canvas.draw()


def UpdateDetails():
    w.details.clear()
    ref = ""
    com = ""
    spe = ""
    dat = ""
    text = ""

    for page_num in range(len(page_ids)):
        if w.radiobuttons[page_num].isChecked():
            break

    data_path = os.path.join(db_path, "data-n2", page_paths[page_num])
    data_path = os.path.normpath(data_path)
    if os.path.exists(data_path):
        datafile = yaml.safe_load(open(data_path, "r", encoding="utf-8").read())
        ref += datafile.get("REFERENCES")
        com += datafile.get("COMMENTS")

        # datafile is dict (key: value pairs); we read the value of the "DATA" key from this dict
        # DATA is a list with single element (dash "-" defines an element of a list!!!)
        # This element ([0]) is a dict again; we read the value of the "data" key from this dict
        dat = datafile.get("DATA")[0].get("data").strip()

        specs_dict = datafile.get("SPECS", {})
        spe = "\n".join([f"{key}: {value}" for key, value in specs_dict.items()])

        if ref != "":
            text  = "<h4>REFERENCES</h4><p>" + ref + "</p>"
        if com != "":
            text += "<h4>COMMENTS</h4><p>" + com + "</p>"
        if spe != "":
            text += "<h4>SPECS</h4><pre>" + spe + "</pre>"
        if dat != "":
            text += "<h4>DATA</h4><pre>" + dat + "</pre>"
        w.details.setHtml(text)

    else:
        text += "<p> Missing file: " + data_path + " </p>"

def UpdateInfo():
    w.info.clear()
    shelf_num = w.combobox1.currentIndex()
    book_num = w.combobox2.currentIndex()
    for page_num in range(len(page_ids)):
        if w.radiobuttons[page_num].isChecked():
            break
    text = ""
    if shelf_info_paths[shelf_num]:
        info_path = os.path.normpath(os.path.join(db_path, "info", shelf_info_paths[shelf_num]))
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as file:
                text += file.read()
        else:
            text += "<p> Missing file: " + info_path + " </p>"
    if book_info_paths[book_num]:
        info_path = os.path.normpath(os.path.join(db_path, "info", book_info_paths[book_num]))
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as file:
                text += file.read()
        else:
            text += "<p> Missing file: " + info_path + " </p>"
    if page_info_paths[page_num]:
        info_path = os.path.normpath(os.path.join(db_path, "info", page_info_paths[page_num]))
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as file:
                text += file.read()
        else:
            text += "<p> Missing file: " + info_path + " </p>"
    w.info.setHtml(text)




def html2mathtext(str):
    str = re.sub(r"<sub>(.*?)</sub>", r"$_{\1}$", str) # subscript
    # str = re.sub(r"<sup>(.*?)</sup>", r"$^{\1}$", str) # superscript
    # str = re.sub(r"<b>(.*?)</b>", r"$\\mathbf{\1}$", str) # bold
    # str = re.sub(r"<i>(.*?)</i>", r"$\\mathit{\1}$", str) # italic
    return f"{str}"
            

#------------------------------------------------------------------------------------------
##PopulateShelfList()
app = QApplication(sys.argv)
w = MainWindow()
w.setWindowTitle("n2 Explorer")
w.show()
UpdateShelfList()
app.exec()
