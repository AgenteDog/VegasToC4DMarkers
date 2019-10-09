# Copyright (c) <year> <author>
"""Name-Us: Vegas to C4D Markers
Description-Us: Helps you export Vegas Pro markers and place them in Cinema 4D.
"""

import c4d
import os


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp


import c4d
from c4d import gui



class VegasToC4DMarkers(c4d.plugins.CommandData):

    PLUGIN_ID = 1053571
    PLUGIN_NAME = 'Vegas To C4D Markers'
    PLUGIN_INFO = 0
    PLUGIN_ICON = load_bitmap('res/icons/vegas-to-c4d-markers.png')
    PLUGIN_HELP = ''

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON,
            self.PLUGIN_HELP, self)

    #Welcome to the world of Python

    def Execute(self, doc):

        #Input xml file location and check if it is an xml file (or if the file exists)
        file_loc = c4d.gui.InputDialog('XML File Location', '')
        if file_loc == '':
            print("Canceled")

        elif file_loc.endswith(".xml") == False:
            gui.MessageDialog('The file you inputed does not end with ".xml"')

        else:
            import xml.etree.ElementTree as ET
            try:
                tree = ET.parse(file_loc)
            except:
                gui.MessageDialog("It seems like the XML file location does not exist...")
            tree = ET.parse(file_loc)
            root = tree.getroot()


            #Parse sequence info
            sequences = []
            sequence = {}
            sequences_number = 0

            for sequences_names in root.findall('project/children/sequence'):
                sequence_name = sequences_names.find('name').text
                sequence_name = str(sequence_name)
                sequence['Name'] = sequence_name
                sequences.append(sequence)
                sequences_number = sequences_number + 1


            #Parse sequence framerate
            sequences_framerates = []
            sequence_framerates = {}

            for sequence_framerate in root.findall('project/children/sequence/rate'):
                sequence_rate = sequence_framerate.find('timebase').text
                sequence_rate = str(sequence_rate)
                sequence_framerates['Rate'] = sequence_rate
                sequences_framerates.append(sequence_framerates)

            #Put the sequences framerate and name in one dict
            sequences_final_info = []
            sequence_final_info = {}

            for name, rate in zip(sequences, sequences_framerates):
                sequence_final_info['Name'] = name['Name']
                sequence_final_info['Rate'] = rate['Rate']
                sequences_final_info.append(sequence_final_info)


            #Parse and use info for selected sequence
            all_info = []
            info = {}
            for sequence_info in sequences_final_info:

                # Parse Markers Info
                markers_found = 0
                frames = ''

                for markers in root.findall('project/children/sequence/marker'):
                    markers_found = markers_found + 1
                    frame = markers.find('in').text
                    frame = str(frame)
                    frames = frames + frame + ','
                frames = frames[:-1]
                if frames == '':
                    gui.MessageDialog("It seems like this project has no markers...")
                else:

                    #Assign sequence and framte of the sequence
                    info['Name'] = sequence_info['Name']
                    info['Framerate'] = sequence_info['Rate']
                    info['MarkerCount'] = str(markers_found)
                    info['MarkerFrames'] = frames
                    all_info.append(info)
                    frames = frames.split(',')

                # Start using all the info to create markers
                fps = doc[c4d.DOCUMENT_FPS]
                #Check if the fps on the c4d project is the same as in the vegas project. If not asks if you would like to change it.
                if fps != float(sequence_rate):
                    change_rate = gui.QuestionDialog("The project framerate is not the same as the Vegas framerate! (" + sequence_rate + ") Would you like to change it? \n \n" + "Yes: Changes fps to " + sequence_rate + " and places all markers. \n" + "No: Cancels the operation.")
                    if change_rate == True:
                        sequence_rate = int(sequence_rate)
                        doc[c4d.DOCUMENT_FPS] = sequence_rate
                        #Open timeline window and start puttings marks
                        c4d.CallCommand(465001541, 465001541) # Timeline (Dope Sheet)...
                        for info in frames:
                            frame = float(info)
                            Time = c4d.BaseTime(frame,fps)
                            doc.SetTime(Time)
                            c4d.EventAdd()
                            c4d.CallCommand(465001124, 465001124) # Create Marker at Current Frame
                        frame = float(info)
                        Time = c4d.BaseTime(0,fps)
                        doc.SetTime(Time)
                        c4d.EventAdd()
                        print("done!")
                    else:
                        c4d.CallCommand(12373) # Project Settings...

                #If the fps on both projects match then continue normally
                else:

                    #Open timeline window and start puttings marks
                    c4d.CallCommand(465001541, 465001541) # Open Timeline (Dope Sheet)...
                    for info in frames:
                        frame = float(info)
                        Time = c4d.BaseTime(frame,fps)
                        doc.SetTime(Time)
                        c4d.EventAdd()
                        c4d.CallCommand(465001124, 465001124) # Create Marker at Current Frame
                    frame = float(info)
                    Time = c4d.BaseTime(0,fps)
                    doc.SetTime(Time)
                    c4d.EventAdd()
                    print("Done!")
        return True
