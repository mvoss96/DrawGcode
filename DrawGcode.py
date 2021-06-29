# requires  Python 3.6.7
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
import math
import sys
import re

warnings.filterwarnings("ignore")  # remove deprecation warnings
plt.rcParams['toolbar'] = 'None'  # remove stock matplotlib toolbar


# Author and information
def print_startup_message():
    print("DrawGcode v0.3b by Marcus Voß\nhttps://git.io/fhTYj\n")
    print("--------------------------------------------")


# print a syntax error if something cant be interpreted
def print_error(type, reason=""):
    print("The following error occured:", type, "(" + reason + ")")


# return the right color based on the pen variable
def linecolor(pen):
    return "blue" if pen else "grey"

# return the right width based on the pen variable
def linewidth(pen):
    return 3 if pen else 0.5

# return the target angle (in degrees) to a point on a circle seen from the center of the circle. dx,dy: relative coordinates of the point from the center. r: Radius of the circle.
def point_angle(dx, dy, r):
    if dy > 0 and dx > 0:
        angle = math.asin(dy / r)
    elif dy > 0 and dx <= 0:
        angle = math.pi / 2 + math.asin(math.fabs(dx) / r)
    elif dy <= 0 and dx < 0:
        angle = math.pi + math.asin(math.fabs(dy) / r)
    else:
        angle = math.pi * 1.5 + math.asin(math.fabs(dx) / r)
    return angle * (180 / math.pi)


# return the key (value) from the given command f.e.  readKey("G1 X10",'X') returns 10
def readKey(command, key):
    if key in command:
        value = ""
        temp = command[command.find(key) + 1:]
        for c in temp:
            if not c.isdigit() and c not in {'.', '-'}:
                break
            else:
                value += c
        if value == "":
            print_error("SYNTAX", "key value must not be empty")
            return -1
        return float(value)
    else:
        print_error("INTERNAL", key + " not in " + command)
        return -1


# read a file filename and plot its content
def file_reader(filename):
    x = 0
    y = 0
    pen = False
    print("opening: " + filename + " ...")
    try:
        file = open(filename, "r")
    except IOError:
        print_error("FILE_NOT_FOUND", "unable to open " + filename)
        return -1
    for line in file:
        print(repr(line))  # print line content including "\n"
        #remove all comments
        if ";" in line:
            line = line.split(";")[0]
        if not line:
            continue

        elif "M400" in line:
            if line.split("M400")[1] != "" and line.split("M400")[1] != "\n":
                print("Warning: characters after M400 are ignored")

        elif "G28" in line:
            plt.plot([x, 0], [y, 0], color=linecolor(pen),linewidth=linewidth(pen))
            x = 0
            y = 0
        elif "M280" in line:
            if "P0" in line and "S" in line:
                s = readKey(line, "S")
                if s >= 40:
                    pen = True
                elif s == 0:
                    pen = False
                else:
                    print_error("SYNTAX", "value for M280 P0 out of range")
        elif "G1" in line:
            tx = x
            ty = y
            if "X" in line:
                tx = readKey(line, "X")
            if "Y" in line:
                ty = readKey(line, "Y")
            if x != None and y != None:
                plt.plot([x, tx], [y, ty], color=linecolor(pen), linewidth=linewidth(pen))
                x = tx
                y = ty
            if "Z" in line:
                print_error("NOT_SUPPORTED", "use M280 to controll the pen")

        elif "G2" in line or "G3" in line:
            tx = x
            ty = y
            i = 0
            j = 0
            if "X" in line:
                tx = readKey(line, "X")
            if "Y" in line:
                ty = readKey(line, "Y")
            if "I" in line:
                i = readKey(line, "I")
            if "J" in line:
                j = readKey(line, "J")
            if "Z" in line:
                print_error("NOT_SUPPORTED", "use M280 to controll the pen")
            centerX = x + i
            centerY = y + j
            radius = math.sqrt(
                (centerX - x)**2 + (centerY - y)**
                2)  #distance between start point and center point
            radius2 = math.sqrt(
                (centerX - tx)**2 +
                (centerY - ty)**2)  #distance beteen end point and center point
            if radius != radius2:  #to reach the end point from the starting point both radii have to be equal
                print_error("SYNTAX","arc not possible")
                return -1
            s1 = point_angle(
                x - centerX, y - centerY,
                radius)  #angle from the center point  to the start point
            s2 = point_angle(
                tx - centerX, ty - centerY,
                radius)  #angle from the center point  to the end point
            if "G2" in line:
                pac = mpatches.Arc([centerX, centerY],
                                   2 * radius,
                                   2 * radius,
                                   angle=0,
                                   theta1=s2,
                                   theta2=s1,
                                   color=linecolor(pen),
                                   linewidth=linewidth(pen))
            else:
                pac = mpatches.Arc([centerX, centerY],
                                   2 * radius,
                                   2 * radius,
                                   angle=0,
                                   theta1=s1,
                                   theta2=s2,
                                   color=linecolor(pen),
                                   linewidth=linewidth(pen))
            ax = plt.gca()
            ax.add_patch(pac)
            x = tx
            y = ty
        else:
            supported_commands = ["G1", "G2", "G3", "G28", "M280", "M400"]
            print_error("NOT_SUPPORTED",
                        "supported commands are: " + str(supported_commands))

    plt.xlim(0, 390)  #the maximum x-dimensions
    plt.ylim(0, 310)  #the maximum y-dimensions
    plt.xlim(0, 297)  #the maximum x-dimensions (A4)
    plt.ylim(0, 210)  #the maximum y-dimensions (A4)
    plt.gca().set_aspect('equal')
    plt.show()


if __name__ == "__main__":
    print_startup_message()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Please input a filename to open: ")
    file_reader(filename)
