# this file is part of refractiveindex.info database
# refractiveindex.info database is in the public domain
# copyright and related rights waived via CC0 1.0

import sys
import yaml
import os
import re

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QComboBox, QCheckBox, QRadioButton, QSpacerItem, QTextBrowser, QTabWidget
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QScrollArea

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


# arrays for library structure and content
shelf_ids = []
shelf_names = []

book_ids = []
book_names = []

page_ids = []
page_names = []
page_paths = []

wl = []
n2 = []

# we assume that this script is in the "tools" directory of the RII database
current_file_path = os.path.abspath(__file__)
db_path = os.path.dirname(os.path.dirname(current_file_path))

lib_path = os.path.join(db_path, "catalog-n2.yml")
with open(lib_path, "r", encoding="utf-8") as file:
    library = yaml.safe_load(file)

fig, ax = plt.subplots()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # spacers for layout alignment
        h_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Shelves and Books combo boxes
        self.combobox1 = QComboBox()
        self.combobox2 = QComboBox()

        # Plot
        self.canvas = FigureCanvas(fig)

        # Detailed output box
        self.details = QTextBrowser()
        self.details.setOpenExternalLinks(True)

        # About box
        self.about = QTextBrowser()
        self.about.setOpenExternalLinks(True)

        # Page checkboxes (added/removed later depending on number of pages)
        self.checkboxes = []
        self.checkboxes_widget = QWidget() #widget to set to scroll area (cannot set layout directly)
        self.checkboxes_layout = QVBoxLayout(self.checkboxes_widget)
        self.checkboxes_layout.addSpacerItem(v_spacer)
        self.checkboxes_scroll = QScrollArea()
        self.checkboxes_scroll.setWidget(self.checkboxes_widget)
        self.checkboxes_scroll.setWidgetResizable(True)

        # Plot checkboxes
        self.plot_checkboxes_layout = QHBoxLayout()
        self.checkbox_LogX = QCheckBox("LogX")
        self.checkbox_LogY = QCheckBox("LogY")
        self.checkbox_LogX.setChecked(False)
        self.checkbox_LogY.setChecked(False)
        self.plot_checkboxes_layout.addSpacerItem(h_spacer)
        self.plot_checkboxes_layout.addWidget(self.checkbox_LogX)
        self.plot_checkboxes_layout.addWidget(self.checkbox_LogY)
        self.plot_checkboxes_layout.addSpacerItem(h_spacer)

        # Page radiobuttons (added/removed later depending on number of pages)
        self.radiobuttons = []
        self.radiobuttons_widget = QWidget() #widget to set to scroll area (cannot set layout directly)
        self.radiobuttons_layout = QVBoxLayout(self.radiobuttons_widget)
        self.radiobuttons_layout.addSpacerItem(v_spacer)
        self.radiobuttons_scroll = QScrollArea()
        self.radiobuttons_scroll.setWidget(self.radiobuttons_widget)
        self.radiobuttons_scroll.setWidgetResizable(True)

        # Tab widget
        tab_widget = QTabWidget()

        # Explorer tab
        tab1 = QWidget()
        tab1_layout = QGridLayout(tab1)
        tab1_layout.addWidget(self.checkboxes_scroll,0,0,2,1)
        tab1_layout.addWidget(self.canvas,0,1,1,1)
        tab1_layout.addLayout(self.plot_checkboxes_layout,1,1,1,1)
        tab1_layout.setColumnStretch(0, 1)
        tab1_layout.setColumnStretch(1, 3)
        tab_widget.addTab(tab1, "Data explorer")

        # Details tab
        tab2 = QWidget()
        tab2_layout = QHBoxLayout(tab2)
        tab2_layout.addWidget(self.radiobuttons_scroll)
        tab2_layout.addWidget(self.details)
        tab2_layout.setStretchFactor(self.radiobuttons_scroll, 1)
        tab2_layout.setStretchFactor(self.details, 3)
        tab_widget.addTab(tab2, "Details")

        # About tab
        tab3 = QWidget()
        tab3_layout = QHBoxLayout(tab3)
        tab3_layout.addWidget(self.about)
        tab_widget.addTab(tab3, "About")

        # populate main_layout (vertical)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.combobox1)
        main_layout.addWidget(self.combobox2)
        main_layout.addWidget(tab_widget)

        window = QWidget()
        window.setLayout(main_layout)

        self.combobox1.currentIndexChanged.connect(UpdateBookList)
        self.combobox2.currentIndexChanged.connect(UpdatePageList)
        self.checkbox_LogX.stateChanged.connect(UpdatePlot)
        self.checkbox_LogY.stateChanged.connect(UpdatePlot)

        self.setCentralWidget(window)



def UpdateShelfList():
    global shelf_name
    shelf_ids = []
    shelf_names = []
    for shelf in library:
        if "SHELF" in shelf:
            shelf_ids.append(shelf.get("SHELF"))
            shelf_names.append(shelf.get("name"))
            w.combobox1.addItem(shelf.get("name"))
        elif "DIVIDER" in shelf:
            shelf_ids.append("")
            shelf_names.append("")
            # add disabled item as divider
            w.combobox1.addItem("   " + shelf.get("DIVIDER"))
            model_item = w.combobox1.model().item(w.combobox1.count()-1)
            model_item.setEnabled(False)
            font = model_item.font()
            font.setBold(True)
            model_item.setFont(font)
            
    # select first enabled item
    for i in range(w.combobox1.count()):
        if w.combobox1.model().item(i).isEnabled():
            w.combobox1.setCurrentIndex(i)
            break

def UpdateBookList():
    global book_ids, book_names

    shelf = library[w.combobox1.currentIndex()].get("content")
    if not shelf:
        return

    w.combobox2.clear()
    book_ids = []
    book_names = []

    for book in shelf:
        if "BOOK" in book:
            book_ids.append(book.get("BOOK"))
            book_names.append(book.get("name"))
            w.combobox2.addItem(re.sub("<[^<]+?>", "", book.get("name"))) # strip HTML tags from name)
        elif "DIVIDER" in book:
            book_ids.append("")
            book_names.append("")
            # add disabled item as divider
            w.combobox2.addItem("   " + book.get("DIVIDER"))
            model_item = w.combobox2.model().item(w.combobox2.count()-1)
            model_item.setEnabled(False)
            font = model_item.font()
            font.setBold(True)
            model_item.setFont(font)
    # select first enabled item
    for i in range(w.combobox2.count()):
        if w.combobox2.model().item(i).isEnabled():
            w.combobox2.setCurrentIndex(i)
            break

def UpdatePageList():
    global page_ids, page_names, page_paths

    shelf = library[w.combobox1.currentIndex()].get("content")
    if not shelf:
        return
    book = shelf[w.combobox2.currentIndex()].get("content")
    if not book:
        return

    page_ids = []
    page_names = []
    page_paths = []
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
            is_first_enabled = (len(page_ids)==1 and page_ids[0]!="") or (len(page_ids)==2 and page_ids[0]=="")
            # add a checked checkbox
            checkbox = QCheckBox(html2mathtext(page.get("name")))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(UpdatePlot)
            w.checkboxes.append(checkbox)
            w.checkboxes_layout.insertWidget(i, checkbox)
            # add a radiobutton and check it if it's the first enabled radiobutton
            radiobutton = QRadioButton(html2mathtext(page.get("name")))
            radiobutton.setStyleSheet("background: white") # workaround to prevent coloring of unchecked radiobuttons
            radiobutton.setChecked(is_first_enabled)
            radiobutton.toggled.connect(UpdateDetails)
            w.radiobuttons.append(radiobutton)
            w.radiobuttons_layout.insertWidget(i, radiobutton)
        if "DIVIDER" in page:
            page_ids.append("")
            page_names.append("")
            page_paths.append("")
            # add a hidden checkbox (label only)
            checkbox = QCheckBox(html2mathtext(page.get("DIVIDER")))
            checkbox.setEnabled(False)
            font = checkbox.font()
            font.setBold(True)
            checkbox.setFont(font)
            checkbox.setStyleSheet("QCheckBox::indicator {width: 0px; border: none;}")
            w.checkboxes.append(checkbox)
            w.checkboxes_layout.insertWidget(i, checkbox)
            # add a hidden radiobutton
            radiobutton = QRadioButton(html2mathtext(page.get("DIVIDER")))
            radiobutton.setEnabled(False)
            font = radiobutton.font()
            font.setBold(True)
            radiobutton.setFont(font)
            radiobutton.setStyleSheet("QRadioButton::indicator {width: 0px; border: none;}")
            w.radiobuttons.append(radiobutton)
            w.radiobuttons_layout.insertWidget(i, radiobutton)
    UpdateData()
    UpdatePlot()
    UpdateDetails()
    UpdateAbout()


def UpdateData():
    global wl, n2
    wl = []
    n2 = []
    for i in range(len(page_ids)):
        if page_ids[i] == "": # DIVIDER
            wl.append(0)
            n2.append(0)
            continue
        data_path = os.path.join(db_path, "data", page_paths[i])
        data_path = os.path.normpath(data_path)
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as file:
                datafile = yaml.safe_load(file)
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
    ax.set_xscale('log' if w.checkbox_LogX.isChecked() else 'linear')
    ax.set_yscale('log' if w.checkbox_LogY.isChecked() else 'linear')
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
    con = ""
    dat = ""
    text = ""

    for page_num in range(len(page_ids)):
        if w.radiobuttons[page_num].isChecked():
            break

    data_path = os.path.join(db_path, "data", page_paths[page_num])
    data_path = os.path.normpath(data_path)
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as file:
            datafile = yaml.safe_load(file)
        ref += datafile.get("REFERENCES")
        com += datafile.get("COMMENTS")

        # datafile is dict (key: value pairs); we read the value of the "DATA" key from this dict
        # DATA is a list with single element (dash "-" defines an element of a list!!!)
        # This element ([0]) is a dict again; we read the value of the "data" key from this dict
        dat = datafile.get("DATA")[0].get("data").strip()

        conditions_dict = datafile.get("CONDITIONS", {})
        con = stringify(conditions_dict)
        
        properties_dict = datafile.get("PROPERTIES", {})
        pro = stringify(properties_dict)

        if con != "":
            text += "<h4>CONDITIONS</h4><pre>" + con + "</pre>"
        if pro != "":
            text += "<h4>PROPERTIES</h4><pre>" + pro + "</pre>"
        if com != "":
            text += "<h4>COMMENTS</h4><p>" + com + "</p>"
        if ref != "":
            text  += "<h4>REFERENCES</h4><p>" + ref + "</p>"
        if dat != "":
            text += "<h4>DATA</h4><pre>" + dat + "</pre>"
        w.details.setHtml(text)

    else:
        text += "<p> Missing file: " + data_path + " </p>"



def UpdateAbout():
    w.about.clear()
    
    for page_num in range(len(page_ids)):
        if w.radiobuttons[page_num].isChecked():
            break
    
    about1 = ''
    names1 = []
    links1 = []
    about2 = ''
    names2 = []
    links2 = []
    text = ''

    data_path = os.path.join(db_path, "data", page_paths[page_num])
    data_path = os.path.normpath(data_path)
    
    datadir = os.path.dirname(page_paths[page_num])
    dir_1up = os.path.dirname(datadir)
    dir_2up = os.path.dirname(dir_1up)
    
    # up to two about.yml files: one or two levels higher in directory tree than the datafile
    about_path1 = os.path.join(db_path, "data", dir_1up, "about.yml")
    about_path2 = os.path.join(db_path, "data", dir_2up, "about.yml")
    
    if os.path.exists(about_path1):
        with open(about_path1, "r", encoding="utf-8") as file:
            aboutfile = yaml.safe_load(file)        
        raw_read = aboutfile.get("NAMES", [[{}]])
        names1 = [str(item) for item in raw_read]
        about1 = aboutfile.get("ABOUT", {})
        raw_read = aboutfile.get("LINKS", [])
        for link in raw_read:
            if 'url' in link and 'text' in link:
                links1.append(f'<a href="{link["url"]}">{link["text"]}</a>')

    if os.path.exists(about_path2):
        with open(about_path2, "r", encoding="utf-8") as file:
            aboutfile = yaml.safe_load(file)        
        raw_read = aboutfile.get("NAMES", [[{}]])
        names2 = [str(item) for item in raw_read]
        about2 = aboutfile.get("ABOUT", {})
        raw_read = aboutfile.get("LINKS", [])
        for link in raw_read:
            if 'url' in link and 'text' in link:
                links2.append(f'<a href="{link["url"]}">{link["text"]}</a>')
    
    if about1 != '' or names1 or links1:
        text += '<h3>About'
        if(names1):
            text += f' {names1[0]}'
        text += '</h3>'
        text += '<div style="margin:0 10px 10px 10px;">'
        if about1 != '':
            text += f'<p>{about1}</p>' 
        if names1 and len(names1) > 1:
            text += f'<h4>Other names and variants of {names1[0]}</h4>'
            text += '<ul>'
            for name in names1[1:]:
                text += f'<li>{name}</li>'
            text += '</ul>'
        if links1:
            text += '<h4>Links</h4>'
            text += '<ul>'
            for link in links1:
                text += f'<li>{link}</li>'
            text += '</ul>'            
        text += '</div>'
    
    if about2 != '' or names2 or links2:
        text += '<h3>About'
        if(names2):
            text += f' {names2[0]}'
        text += '</h3>'
        text += '<div style="margin:0 10px 10px 10px;">'
        if about2 != '':
            text += f'<p>{about2}</p>'
        if names2 and len(names2) > 1:
            text += f'<h4>Other names and variants of {names2[0]}</h4>'
            text += '<ul>'
            for name in names2[1:]:
                text += f'<li>{name}</li>'
            text += '</ul>'
        if links2:
            text += '<h4>Links</h4>'
            text += '<ul>'
            for link in links2:
                text += f'<li>{link}</li>'
            text += '</ul>'
        text += '</div>'
            
    w.about.setHtml(text)




def html2mathtext(str):
    str = re.sub(r"<sub>(.*?)</sub>", r"$_{\1}$", str) # subscript
    # str = re.sub(r"<sup>(.*?)</sup>", r"$^{\1}$", str) # superscript
    # str = re.sub(r"<b>(.*?)</b>", r"$\\mathbf{\1}$", str) # bold
    # str = re.sub(r"<i>(.*?)</i>", r"$\\mathit{\1}$", str) # italic
    return f"{str}"



def stringify(d, indent=0):
    s = ""
    for i, (key, value) in enumerate(d.items()):
        if i>0:
            s += "\n"
        s += " "*indent + f"{key}:"
        if isinstance(value, dict):
            s += "\n" + stringify(value, indent+2)
        elif isinstance(value, list) and all(isinstance(ii, dict) for ii in value):
            for item in value:
                s += "\n  - " + stringify(item, indent+4).lstrip()
        else:
            s += f" {value}"
    return s


#------------------------------------------------------------------------------------------
app = QApplication(sys.argv)
w = MainWindow()
w.setWindowTitle("n2 Explorer - Refractiveindex.info")
w.show()
UpdateShelfList()
app.exec()
