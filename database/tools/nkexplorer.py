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

import numpy as np

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

wl_n = []
wl_k = []
n = []
k = []
n_defined = []
k_defined = []

# we assume that this script is in the "tools" directory of the RII database
current_file_path = os.path.abspath(__file__)
db_path = os.path.dirname(os.path.dirname(current_file_path))

lib_path = os.path.join(db_path, "catalog-nk.yml")
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
        self.checkbox_n = QCheckBox("n")
        self.checkbox_k = QCheckBox("k")
        self.checkbox_LogX = QCheckBox("LogX")
        self.checkbox_LogY = QCheckBox("LogY")
        self.checkbox_n.setChecked(True)
        self.checkbox_k.setChecked(True)
        self.checkbox_LogX.setChecked(False)
        self.checkbox_LogY.setChecked(False)
        self.plot_checkboxes_layout.addSpacerItem(h_spacer)
        self.plot_checkboxes_layout.addWidget(self.checkbox_n)
        self.plot_checkboxes_layout.addWidget(self.checkbox_k)
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
        self.checkbox_n.stateChanged.connect(UpdatePlot)
        self.checkbox_k.stateChanged.connect(UpdatePlot)
        self.checkbox_LogX.stateChanged.connect(UpdatePlot)
        self.checkbox_LogY.stateChanged.connect(UpdatePlot)

        self.setCentralWidget(window)



def UpdateShelfList():
    global shelf_names
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
            # add a checkbox and check if it's the first enabled checkbox
            checkbox = QCheckBox(html2mathtext(page.get("name")))
            checkbox.setChecked(is_first_enabled)
            checkbox.stateChanged.connect(UpdatePlot)
            w.checkboxes.append(checkbox)
            w.checkboxes_layout.insertWidget(i, checkbox)
            # add a radiobutton and check if it's the first enabled radiobutton
            radiobutton = QRadioButton(html2mathtext(page.get("name")))
            #radiobutton.setStyleSheet("background: white") # workaround to prevent coloring of unchecked radiobuttons
            radiobutton.setChecked(is_first_enabled)
            radiobutton.toggled.connect(UpdateDetails)
            radiobutton.toggled.connect(UpdateAbout)
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
    global wl_n, wl_k, n, k, n_defined, k_defined
    wl_n = []
    wl_k = []
    n = []
    k = []
    n_defined = []
    k_defined = []
    for i in range(len(page_ids)):
        if page_ids[i] == "": # DIVIDER
            n_defined.append(False)
            k_defined.append(False)
            wl_n.append(0)
            wl_k.append(0)
            n.append(0)
            k.append(0)
            continue
        data_path = os.path.join(db_path, "data", page_paths[i])
        data_path = os.path.normpath(data_path)
        if os.path.exists(data_path):
            tmp_wl_n = []
            tmp_wl_k = []
            tmp_n = []
            tmp_k = []
            tmp_n_defined = False
            tmp_k_defined = False
            with open(data_path, "r", encoding="utf-8") as file:
                datafile = yaml.safe_load(file)
            for data in datafile.get("DATA"):
                datatype = data.get("type").split()
                if datatype[0] == "tabulated":
                    rows = data.get("data").split("\n")
                    splitrows = [c.split() for c in rows]
                    for s in splitrows:
                        if len(s) > 0:
                            if datatype[1] == "n":
                                tmp_n_defined = True
                                tmp_wl_n.append(float(s[0]))
                                tmp_n.append(float(s[1]))
                            if datatype[1] == "k":
                                tmp_k_defined = True
                                tmp_wl_k.append(float(s[0]))
                                tmp_k.append(float(s[1]))
                            if datatype[1] == "nk":
                                tmp_n_defined = True
                                tmp_k_defined = True
                                tmp_wl_n.append(float(s[0]))
                                tmp_wl_k.append(float(s[0]))
                                tmp_n.append(float(s[1]))
                                tmp_k.append(float(s[2]))
                elif datatype[0] == "formula":
                    tmp_n_defined = True
                    wavelength_range = np.array(data.get("wavelength_range").split()).astype(float)
                    if wavelength_range[1]/wavelength_range[0] > 20:
                        wl = np.logspace(np.log10(wavelength_range[0]), np.log10(wavelength_range[1]), 101)
                    else:
                        wl = np.linspace(wavelength_range[0], wavelength_range[1], 101)
                    tmp_wl_n = wl
                    coefficients = np.array(data.get("coefficients").split()).astype(float)
                    num_coeff = coefficients.size
                    C1  = coefficients[0] if num_coeff>0 else 0
                    C2  = coefficients[1] if num_coeff>1 else 0
                    C3  = coefficients[2] if num_coeff>2 else 0
                    C4  = coefficients[3] if num_coeff>3 else 0
                    C5  = coefficients[4] if num_coeff>4 else 0
                    C6  = coefficients[5] if num_coeff>5 else 0
                    C7  = coefficients[6] if num_coeff>6 else 0
                    C8  = coefficients[7] if num_coeff>7 else 0
                    C9  = coefficients[8] if num_coeff>8 else 0
                    C10  = coefficients[9] if num_coeff>9 else 0
                    C11  = coefficients[10] if num_coeff>10 else 0
                    C12  = coefficients[11] if num_coeff>11 else 0
                    C13  = coefficients[12] if num_coeff>12 else 0
                    C14  = coefficients[13] if num_coeff>13 else 0
                    C15  = coefficients[14] if num_coeff>14 else 0
                    C16  = coefficients[15] if num_coeff>15 else 0
                    C17  = coefficients[16] if num_coeff>16 else 0
                    if datatype[1] == "1":
                        tmp_n = (1 + C1 + C2/(1-(C3/wl)**2) + C4/(1-(C5/wl)**2) + C6/(1-(C7/wl)**2)
                                        + C8/(1-(C9/wl)**2) + C10/(1-(C11/wl)**2) + C12/(1-(C13/wl)**2)
                                        + C14/(1-(C15/wl)**2) + C16/(1-(C17/wl)**2))**0.5
                    elif datatype[1] == "2":
                        tmp_n = (1 + C1 + C2/(1-C3/wl**2) + C4/(1-C5/wl**2) + C6/(1-C7/wl**2)
                                        + C8/(1-C9/wl**2) + C10/(1-C11/wl**2) + C12/(1-C13/wl**2)
                                        + C14/(1-C15/wl**2) + C16/(1-C17/wl**2))**0.5
                    elif datatype[1] == "3":
                        tmp_n = (C1 + C2*wl**C3 + C4*wl**C5 + C6*wl**C7 + C8*wl**C9 + C10*wl**C11
                                 + C12*wl**C13 + C14*wl**C15 + C16*wl**C17)**0.5
                    elif datatype[1] == "4":
                        tmp_n = (C1 + C2*wl**C3/(wl**2-C4**C5) + C6*wl**C7/(wl**2-C8**C9)
                                 + C10*wl**C11 + C12*wl**C13 + C14*wl**C15 + C16*wl**C17)**0.5
                    elif datatype[1] == "5":
                        tmp_n = C1 + C2*wl**C3 + C4*wl**C5 + C6*wl**C7 + C8*wl**C9 + C10*wl**C11
                    elif datatype[1] == "6":
                        tmp_n = 1 + C1 + C2/(C3-wl**-2) + C4/(C5-wl**-2) + C6/(C7-wl**-2) + C8/(C9-wl**-2) + C10/(C11-wl**-2)
                    elif datatype[1] == "7":
                        tmp_n = C1 + C2/(wl**2-0.028) + C3/(wl**2-0.028)**2 + C4*wl**2 + C5*wl**4 + C6*wl**6
                    elif datatype[1] == "8":
                        tmp = C1 + C2*wl**2/(wl**2-C3) + C4*wl**2
                        tmp_n = ((2*tmp+1)/(1-tmp))**0.5
                    elif datatype[1] == "9":
                        tmp_n = (C1 + C2/(wl**2-C3) + C4*(wl-C5)/((wl-C5)**2 + C6))**0.5

        n_defined.append(tmp_n_defined)
        k_defined.append(tmp_k_defined)
        wl_n.append(tmp_wl_n)
        wl_k.append(tmp_wl_k)
        n.append(tmp_n)
        k.append(tmp_k)




def UpdatePlot():
    ax.clear()
    for i in range(len(page_ids)):
        if w.checkboxes[i].isChecked():
            first_curve_plotted = False
            if n_defined[i] == True and w.checkbox_n.isChecked():
                line, = ax.plot(wl_n[i], n[i], label=page_ids[i])
                first_curve_plotted = True
            if k_defined[i] == True and w.checkbox_k.isChecked():
                # Plot with dashed line and same color as first curve
                # If both curves are enabled, don't add a new label
                if first_curve_plotted:
                    ax.plot(wl_k[i], k[i], linestyle='--', color=line.get_color())
                else:
                    ax.plot(wl_k[i], k[i], linestyle='--', label=page_ids[i])
    ax.set_xscale('log' if w.checkbox_LogX.isChecked() else 'linear')
    ax.set_yscale('log' if w.checkbox_LogY.isChecked() else 'linear')
    ax.set_title(html2mathtext(book_names[w.combobox2.currentIndex()]))
    ax.set_xlabel("Wavelength (μm)")
    if w.checkbox_n.isChecked() and not w.checkbox_k.isChecked():
        ax.set_ylabel("n")
    elif w.checkbox_k.isChecked() and not w.checkbox_n.isChecked():
        ax.set_ylabel("k")
    else:
        ax.set_ylabel("n (solid), k (dashed)")
    ax.grid()
    ax.legend()
    fig.tight_layout()
    w.canvas.draw()



def UpdateDetails():
    w.details.clear()
    ref = ""
    com = ""
    con = ""
    pro = ""
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
        ref += datafile.get("REFERENCES", "")
        com += datafile.get("COMMENTS", "")

        # datafile is dict (key: value pairs); we read the value of the "DATA" key from this dict
        # DATA is a list with single element (dash "-" defines an element of a list!!!)
        # This element ([0]) is a dict again; we read the value of the "data" key from this dict
        for data in datafile.get("DATA"):
            if dat != "":
                dat += "\n\n"
            datatype = data.get("type").split()
            dat += "<b>type: " + datatype[0] + " " + datatype[1] + "</b>\n"
            if datatype[0] == "tabulated":
                dat += data.get("data").strip()
            if datatype[0] == "formula":
                dat += "wavelength_range: " + data.get("wavelength_range").strip() + "\n"
                dat += "coefficients: " + data.get("coefficients").strip()


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
w.setWindowTitle("nk Explorer - Refractiveindex.info")
w.show()
UpdateShelfList()
app.exec()
