#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MA builder 

This program loads an xml aircraft and builds it

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: December 2013
"""

import sys
import os.path
import xml.etree.ElementTree as ET

try:
    import ac3d
    import contour
    from wing import Wing
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[
0]+'/../lib'))
    import ac3d
    import contour
    from wing import Wing


def get_value(xml, name):
    e = xml.find(name)
    if e != None and e.text != None:
        return e.text
    else:
        return ""

class Builder():

    def __init__(self, initfile):
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)
        self.load(initfile)

    def parse_overview(self, node):
        self.units = get_value(node, 'units')

    def parse_leading_edge(self, wing, node):
        size = float(get_value(node, 'size'))
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_leading_edge(size=size, start_station=start, end_station=end, part="wing")

    def parse_trailing_edge(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        shape = get_value(node, 'shape').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_trailing_edge(width=width, height=height, shape=shape, start_station=start, end_station=end, part="wing")

    def parse_spar(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        surface = get_value(node, 'surface').lower()
        orientation = get_value(node, 'orientation').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_spar(surf=surface, orientation=orientation, percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ysize=height, start_station=start, end_station=end, part="wing")

    def parse_wing(self, node):
        wing = Wing(get_value(node, 'name'))
        wing.units = self.units
        wing.load_airfoils(get_value(node, 'airfoil'))
        wing.span = float(get_value(node, 'span'))
        station_list = map( float, str(get_value(node, 'stations')).split())
        wing.set_stations( station_list )
        wing.twist = float(get_value(node, 'twist'))
        wing.set_sweep_angle( float(get_value(node, 'sweep')) )
        wing.set_chord( float(get_value(node, 'chord')) )
        wing.dihedral = float(get_value(node, 'dihedral'))
        for le_node in node.findall('leading-edge'):
            self.parse_leading_edge(wing, le_node)
        for te_node in node.findall('trailing-edge'):
            self.parse_trailing_edge(wing, te_node)
        for spar_node in node.findall('spar'):
            self.parse_spar(wing, spar_node)
        #for stringer_node in node.findall('stringer'):
        #    self.parse_stringer(wing, stringer_node)
        #for sheet_node in node.findall('sheet'):
        #    self.parse_sheet(wing, sheet_node)
        #for hole_node in node.findall('simple-hole'):
        #    self.parse_simple_hole(wing, hole_node)
        #for hole_node in node.findall('shaped-hole'):
        #    self.parse_shaped_hole(wing, hole_node)
        #for tab_node in node.findall('build-tab'):
        #    self.parse_build_tab(wing, tab_node)

        wing.build()
        wing.layout_parts_sheets( 24, 8 )
        wing.layout_parts_templates( 8.5, 11 )
        wing.layout_plans( 24, 36 )

        ac = ac3d.AC3D("3dmodel")
        ac.gen_headers( "airframe", 2 )
        wing.build_ac3d( ac )
        ac.close()

    def load(self, filename):
        if not os.path.exists(filename):
            print "Error, design not found: " + filename
            return

        try:
            self.xml = ET.parse(filename)
        except:
            print filename + ": xml parse error:\n" + str(sys.exc_info()[1])
            return

        self.fileroot, ext = os.path.splitext(filename)

        root = self.xml.getroot()

        node = root.find('overview')
        self.parse_overview(node)

        for wing_node in root.findall('wing'):
            self.parse_wing(wing_node)


def usage():
    print "Usage: " + sys.argv[0] + " design.mad"

def main():
    initfile = ""
    if len(sys.argv) != 2:
        usage()
        return
    else:
        initfile = sys.argv[1]
    build = Builder(initfile)

if __name__ == '__main__':
    main()