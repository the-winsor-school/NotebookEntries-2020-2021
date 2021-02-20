import csv
import itertools
import os
import subprocess
import calendar

# Boilerplate LaTeX formatting, including the header with all the package setup and color definitions
header = "\documentclass[16pt]{extarticle} \usepackage[margin=0.6in]{geometry} \usepackage{tikz,lipsum,lmodern} \usepackage[most]{tcolorbox} \\tcbuselibrary{listings,breakable} \usepackage[default]{lato} \usepackage[T1]{fontenc} \usepackage{tikz} \usepackage{dashrule} \usepackage{comment} \usepackage{eso-pic} \usepackage{ifthen} \usepackage{changepage} \usepackage{xcolor} \definecolor{customBlack}{RGB}{46,50,48} \definecolor{buildBlue}{RGB}{198,214,230} \definecolor{codeBlue}{RGB}{211,237,237} \definecolor{businessBlue}{RGB}{156,202,202} \definecolor{lineBlue}{RGB}{0,89,89} \definecolor{textGrey}{RGB}{84,84,84} \definecolor{nameGrey}{RGB}{217,217,217} \definecolor{wholeBlue}{RGB}{188, 217, 223} \color{textGrey} \\renewcommand{\\baselinestretch}{1.3} \\thispagestyle{empty} \\begin{document}"
header += "\AddToShipoutPicture{ \checkoddpage \ifoddpage \put(0,0){\includegraphics[width=\paperwidth]{../figs/oddPage2.png}} \else     \put(0,0){\includegraphics[width=\paperwidth]{../figs/evenPage.png}} \\fi }"
footer = "\end{document}"

def readCSV():
    # Read in each CSV file and create a list of dictionaries
    with open("data/business.csv") as afile:
        businessFile = csv.DictReader(afile)
        businessData = list(businessFile)

    with open("data/building.csv") as bfile:
        buildFile = csv.DictReader(bfile)
        buildData = list(buildFile)

    with open("data/coding.csv") as cfile:
        codingFile = csv.DictReader(cfile)
        codingData = list(codingFile)

    with open("data/wholeTeam.csv") as wfile:
        wholeFile = csv.DictReader(wfile)
        wholeData = list(wholeFile)

    return (businessData, buildData, codingData, wholeData)

def computeDateList(businessData, buildData, codingData, wholeData): 
    # Gather up a master list of all of dates of meetings by reading through every entry
    aDates = [businessData[i]['Date'].split(" ")[0] for i in xrange(len(businessData))]
    bDates = [buildData[i]['Date'].split(" ")[0] for i in xrange(len(buildData))] 
    cDates = [codingData[i]['Date'].split(" ")[0] for i in xrange(len(codingData))]
    wDates = [wholeData[i]['Date'].split(" ")[0] for i in xrange(len(wholeData))]
    # Taking the set removes duplicates. Then return an unsorted list
    allDates = list(set(aDates + bDates + cDates + wDates))
    return allDates

def buildBlock(data, i):
    # "data" is the text, "i" is "Afternoon" or "Morning". 
    # If we have text (i.e. someone wrote something), create a LaTeX color box of the correct color, with a subtitle label and the text
    if len(data) == 0: 
        return ''
    else:
        return "\\begin{tcolorbox}[colback=buildBlue,colframe=white!,coltext=textGrey]  \\textit{\\textbf{Building (" + str(i) + "): }}" + data + "\end{tcolorbox}"

def codingBlock(data, i):
    # "data" is the text, "i" is "Afternoon" or "Morning". 
    # If we have text (i.e. someone wrote something), create a LaTeX color box of the correct color, with a subtitle label and the text
    if len(data) == 0:
        return 0
    else: 
        return "\\begin{tcolorbox}[colback=codeBlue,colframe=white!,coltext=textGrey]  \\textit{\\textbf{Coding (" + str(i) + "): }} " + data + "\end{tcolorbox}"

def businessBlock(data, i):
    # "data" is the text, "i" is "Afternoon" or "Morning". 
    # If we have text (i.e. someone wrote something), create a LaTeX color box of the correct color, with a subtitle label and the text
    if len(data) == 0: 
        return ''
    else:
        return "\\begin{tcolorbox}[colback=businessBlue,colframe=white!,coltext=textGrey]  \\textit{\\textbf{Business (" + str(i) + "): }}" + data + "\end{tcolorbox}"

def wholeBlock(data, i):
    # "data" is the text, "i" is "Afternoon" or "Morning". 
    # If we have text (i.e. someone wrote something), create a LaTeX color box of the correct color, with a subtitle label and the text
    if len(data) == 0:
        return ''
    else:
        return "\\begin{tcolorbox}[colback=wholeBlue,colframe=white!,coltext=textGrey]  \\textit{\\textbf{Entire Team: }}" + data + "\end{tcolorbox}"


def findIndicesForDate(allData, date):
    # For a given date, find all of the entries in allData that correspond to that date. 
    matching = []
    for i in xrange(len(allData)):
        rawDay = allData[i]['Date'].split(" ")[0]
        if rawDay == date:
            matching.append(i)
    return matching  

def labelDateCategory(data, idx):
    # Read in the data and create a "date label" for each entry. Specifically, 
    # determine if its a morning or afternoon entry. Also, number the entry
    m = 1
    a = 1
    times = []
    for i in idx:
        dates = data[i]['Date'].split(" ")
        if len(dates) > 1:
            if dates[1][1] == 'm':
                times += ['Morning Group {}'.format(m)]
                m += 1
            else:
                times += ['Afternoon Group {}'.format(a)]
                a += 1
        else:
            times += ['Morning Group {}'.format(m)]
            m += 1
    return times 

def displayDate(date):
    # Convert the date format. i.e. "12/7/2020" -> December 7, 2020
    [m, d, y] = date.split("/")
    return calendar.month_name[int(m)] + ' ' + d + ', ' + y

def generateLatex(businessData, buildData, codingData, wholeData, meeting_date):
    # For a particular meeting_data, generate the corresponding LaTeX page and write to meeting_date.tex
    # There is a lot of list comprehension because each subteam may have multiple entries per date

    # Find the list indices for all the entries corresponding to this date
    aidx = findIndicesForDate(businessData, meeting_date)
    bidx = findIndicesForDate(buildData, meeting_date)
    cidx = findIndicesForDate(codingData, meeting_date)
    widx = findIndicesForDate(wholeData, meeting_date)
    # Create boolean flag for if this subteam has any entries for this date
    aIs = (len(aidx) > 0)
    bIs = (len(bidx) > 0)
    cIs = (len(cidx) > 0)
    wIs = (len(widx) > 0)
    
    # Gather the members listed for any of the entries for this date
    apeople = list(itertools.chain(*[businessData[pa]['Members'].split(', ') for pa in aidx]))
    bpeople = list(itertools.chain(*[buildData[pb]['Members'].split(', ') for pb in bidx]))
    cpeople = list(itertools.chain(*[codingData[pc]['Members'].split(', ') for pc in cidx]))
    wpeople = list(itertools.chain(*[wholeData[pw]['Members'].split(', ') for pw in widx]))
    # By creating a set, this removes duplicates. Then create a writeable list, comma separated
    people =  ", ".join(list(set(apeople + bpeople + cpeople + wpeople)))

    # Generate the morning/afternoon labels for each of the entries for this date
    atimes = labelDateCategory(businessData, aidx)
    btimes = labelDateCategory(buildData, bidx)
    ctimes = labelDateCategory(codingData, cidx)
    wtimes = labelDateCategory(wholeData, widx)

    # Crate a nicely formatted date
    date_pretty = displayDate(meeting_date)
    # Generate the header block with the date and members list
    date = "\\begin{tcolorbox}[colback=customBlack,colframe=white!,coltext=white,sidebyside, lower separated=false, after skip=20pt plus 2pt]  {\Huge " + date_pretty + "}   \\tcblower  \\begingroup      \\fontsize{11.9pt}{10pt}\selectfont      \\textcolor{nameGrey}{ATTENDEES: " + people + "}  \endgroup \end{tcolorbox}"

    # For each of our three headers, write the header (including the dotted line)
    # Then, within each header, if that subteam has entries, generate the color box for each entry

    focus = "{\Large \\textbf{FOCUS }} \\textcolor{lineBlue}{\hdashrule[0.5ex]{16.1cm}{0.5mm}{2mm 1.5pt}}"
    if bIs: focus += " ".join([buildBlock(buildData[bidx[fb]]['Focus'], btimes[fb]) for fb in xrange(len(bidx))])
    if cIs: focus += " ".join([codingBlock(codingData[cidx[fc]]['Focus'], ctimes[fc]) for fc in xrange(len(cidx))])
    if aIs: focus += " ".join([businessBlock(businessData[aidx[fa]]['Focus'], atimes[fa]) for fa in xrange(len(aidx))])
    if wIs: focus += " ".join([wholeBlock(wholeData[widx[fw]]['Focus'], wtimes[fw]) for fw in xrange(len(widx))])

    summary = "{\Large \\textbf{SUMMARY }} \\textcolor{lineBlue}{\hdashrule[0.5ex]{15.2cm}{0.5mm}{2mm 1.5pt}}"
    if bIs: summary += " ".join([buildBlock(buildData[bidx[sb]]['Summary'], btimes[sb]) for sb in xrange(len(bidx))])
    if cIs: summary += " ".join([codingBlock(codingData[cidx[sc]]['Summary'], ctimes[sc]) for sc in xrange(len(cidx))])
    if aIs: summary += " ".join([businessBlock(businessData[aidx[sa]]['Summary'], atimes[sa]) for sa in xrange(len(aidx))])
    if wIs: summary += " ".join([wholeBlock(wholeData[widx[sw]]['Summary'], wtimes[sw]) for sw in xrange(len(widx))])

    challenges = "{\Large \\textbf{CHALLENGES }} \\textcolor{lineBlue}{\hdashrule[0.5ex]{14.7cm}{0.5mm}{2mm 1.5pt}}" 
    if bIs: challenges += " ".join([buildBlock(buildData[bidx[cb]]['Challenges/Problems'], btimes[cb]) for cb in xrange(len(bidx))])
    if cIs: challenges += " ".join([codingBlock(codingData[cidx[cc]]['Challenges/Problems'], ctimes[cc]) for cc in xrange(len(cidx))])
    if aIs: challenges += " ".join([businessBlock(businessData[aidx[ca]]['Challenges/Problems'], atimes[ca]) for ca in xrange(len(aidx))])
    if wIs: challenges += " ".join([wholeBlock(wholeData[widx[cw]]['Challenges/Problems'], wtimes[cw]) for cw in xrange(len(widx))])

    nextSteps = "{\Large \\textbf{NEXT STEPS }} \\textcolor{lineBlue}{\hdashrule[0.5ex]{15cm}{0.5mm}{2mm 1.5pt}}"
    if bIs: nextSteps += " ".join([buildBlock(buildData[bidx[nb]]['Next Steps'], btimes[nb]) for nb in xrange(len(bidx))])
    if cIs: nextSteps += " ".join([codingBlock(codingData[cidx[nc]]['Next Steps'], ctimes[nc]) for nc in xrange(len(cidx))])
    if aIs: nextSteps += " ".join([businessBlock(businessData[aidx[na]]['Next Steps'], atimes[na]) for na in xrange(len(aidx))])
    if wIs: nextSteps += " ".join([wholeBlock(wholeData[widx[nw]]['Next Steps'], wtimes[nw]) for nw in xrange(len(widx))])

    # Gather all of the material in order. "material" is a string file that contains the entire LaTeX document
    material = header + date + focus + summary + challenges + nextSteps + footer

    # Need to reformat date to not use backslashes in the filename
    save_date = meeting_date.replace('/', '_')
    fileName = 'pages/{}.tex'.format(save_date)

    # Write LaTex 
    f = open(fileName, 'a')
    f.write(material)
    f.close()

    return save_date

def generatePDF(fileName):
    # Generate PDF
    # Use subprocess instead of os.system so that we can operate in different directory
    p = subprocess.Popen(['pdflatex', '{}.tex'.format(fileName)], cwd='pages/')
    p.wait()

    # Command to convert to pngs: pdftoppm 9_26_2020.pdf 9_26_2020 -png
    p = subprocess.Popen(['pdftoppm', '{}.pdf'.format(fileName), fileName, '-png'], cwd='pages/')

if __name__ == '__main__':
    # Read in the data
    aData, bData, cData, wData = readCSV()
    # Create the master date list
    dateList = computeDateList(aData, bData, cData, wData)

    # For each date, create the file
    for i in xrange(len(dateList)):
        # This generates the latex file
        fileName = generateLatex(aData, bData, cData, wData, dateList[i])
        # This generates the pdf and then the png
        generatePDF(fileName)
