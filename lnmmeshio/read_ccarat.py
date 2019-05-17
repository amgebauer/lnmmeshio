#
# Maintainer: Amadeus Gebauer
#

import re
import sys
import argparse

SECTIONS_CHANGE_NOT_2_STYLE = ['ARTERY ELEMENTS', 'ALE ELEMENTS','CURVE1','CURVE2','CURVE3','CURVE4','CLONING MATERIAL MAP','DNODE-NODE TOPOLOGY','DLINE-NODE TOPOLOGY','DSURF-NODE TOPOLOGY','DVOL-NODE TOPOLOGY',
                               'ELECTRODE KINETICS LINE CONDITIONS','ELECTRODE KINETICS SURF CONDITIONS','FLUID ELEMENTS','FLUID TURBULENT INFLOW VOLUME', 'COMBUST BLEND MATERIAL VOLUME', 'FLUID NEUMANN INFLOW LINE CONDITIONS',
                               'FLUID NEUMANN INFLOW SURF CONDITIONS','FLUID NEUMANN INFLOW SURF CONDITIONS', 'FILAMENT NUMBERS', 'FORCE SENSORS','FUNCT1','FUNCT2', 'FUNCT3','FUNCT4','MATERIALS','MICROSCALE CONDITIONS',
                               'NODE COORDS','REINITIALIZATION TAYLOR GALERKIN SURF CONDITIONS','RESULT DESCRIPTION','SCATRA FLUX CALC LINE CONDITIONS','SCATRA FLUX CALC SURF CONDITIONS','STRUCTURE ELEMENTS',
                               'SURFACTANT CONDITIONS','SURFACE TENSION CONDITIONS','TAYLOR GALERKIN OUTFLOW SURF CONDITIONS','TAYLOR GALERKIN NEUMANN INFLOW SURF CONDITIONS','TITLE','THERMO ELEMENTS',
                               'TRANSPORT NEUMANN INFLOW LINE CONDITIONS','TRANSPORT NEUMANN INFLOW SURF CONDITIONS','TRANSPORT ELEMENTS'
 ]

def myprint(myfile, mymessage):
    try:
        for i in range(len(mymessage)-1):
            print(mymessage[i], file=myfile, end=' ')
        print(mymessage[-1], file=myfile)
    except TypeError:
        raise Exception('In the following line exist a non-string element\n{0}'.format(mymessage))


def read_ccarat(filename, ig_comm=True, ig_head=True):
    section_names = []
    sections = {}
    sections['header']=[]

    name_re = re.compile('^-+([^-].+)$')
    name = None

    with open(filename, 'r') as file:
        for l in file:
            line = l.strip()
            # catch empty lines
            if not line:
                continue

            match = name_re.match(line)
            if match:
                if line[:2] == '//' and ig_comm:
                    continue
                name = match.group(1)
                section_names.append(name)
                #internal = name.lower().replace(' ', '_')
                sections[name] = []
            elif name:
                if line[:2] == '//' and ig_comm:
                    continue
                sections[name].append(line.split())
            elif not ig_head:
                sections['header'].append(line.split())


    return section_names, sections

def write_ccarat(filename, section_names, sections):
    with open(filename, 'w') as f:
        if 'header' in sections:
            for line in sections['header']:
                print(" ".join(line), file=f)
    
        for name in section_names:
            print("-"*(76-len(name)) + name, file=f)
            sec = sections[name]
            for line in sec:

                if len(line)==2 and name[:min(6, len(name))] != 'TITLE':
                    myprint(f, [line[0]," "*(30-len(line[0])),line[1] ])
            
                elif name in SECTIONS_CHANGE_NOT_2_STYLE:
                    myprint ( f, line )

                #if  and line[0] not in ["END","LAYER:","Non"] and name not in SECTIONS_CAHNGE_NOT_2_STYLE and name[:min(6, len(name))] != 'DESIGN':
                    
                else:
                    # excluded from style edit
                    if (name[:min(6, len(name))] == 'DESIGN' or name in SECTIONS_CHANGE_NOT_2_STYLE):
                        myprint(f, [" ".join(line)])
                    else:
                        # treatment of comment
                        for li, l in enumerate(line):
                            if '//' in l:
                                comment_index = li
                                line2print = [line[0]," "*(30-len(line[0]))," ".join(line[1:comment_index])," "*(30-sum([len(line[i])+1 for i in range(1,comment_index)])-1)," ".join(line[comment_index:])]
                                break
                            else:
                                comment_index = len(line)
                                line2print = [line[0]," "*(30-len(line[0]))," ".join(line[1:comment_index])]
                        myprint ( f, line2print )

def getparam(section,name):
    for line in section:
        if line[0]==name:
            return line[1]
    return None

def setparam(section,name,value):
    found = False
    for line in section:
        if line[0]==name:
            line[1] = value
            found = True
    if not found:
        section.append([name,value])

def Update_PROBLEM_SIZE(sections):
    max_ele = 0
    for field in ['TRANSPORT ELEMENTS', 'STRUCTURE ELEMENTS']:
        if field in sections:
            max_ele = max_ele + len(sections[field])

    setparam(sections['PROBLEM SIZE'], 'ELEMENTS', max_ele )
    setparam(sections['PROBLEM SIZE'], 'NODES', repr(len(sections['NODE COORDS'])) )

def Update_DESIGN_DESCRIPTION(sections):
    for top, name in zip( ['DNODE-NODE TOPOLOGY', 'DLINE-NODE TOPOLOGY', 'DSURF-NODE TOPOLOGY', 'DVOL-NODE TOPOLOGY'],
                          ['NDPOINT'            , 'NDLINE'             , 'NDSURF'             , 'NDVOL'             ]
                          ):
        if top in sections:
            setparam(sections['DESIGN DESCRIPTION'], name, repr(len(sections[top])) )

if __name__ == '__main__':

    # create parser for input arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="Read class for *.dat file.")

    parser.add_argument('infile', help='.dat BACI input file')
    parser.add_argument('--ig_comm', action='store_true', help='ignore comments in file')
    parser.add_argument('--ig_head', action='store_true', help='ignore file head')
    
    # read input arguments
    par = parser.parse_args()

    INPUT          = par.infile
    IG_COMM = par.ig_comm
    IG_HEAD = par.ig_head

    section_names, sections = read_ccarat(INPUT, IG_COMM, IG_HEAD)

    write_ccarat(INPUT + ".cpy", section_names, sections)
