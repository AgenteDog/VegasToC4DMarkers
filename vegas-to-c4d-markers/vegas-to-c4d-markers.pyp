# Copyright (c) <year> <author>
"""Name-Us: Vegas to C4D Markers
Description-Us: Helps you export Vegas Pro markers and place them in Cinema 4D.
"""

# TODO: Remove redundant `if __name__ == '__main__':` check if it was in your script
# TODO: Remove redundant imports
# TODO: Update Copyright information
# TODO: Add a README file
# TODO: Keep in mind that the variables `doc` and `op` are no longer globally available

import c4d
import os


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp


#Made by Agente Dog - 10/9/2019 - 14 y/o

import c4d
from c4d import gui
import xml.etree.ElementTree as ET



class VegastoC4DMarkers(c4d.plugins.CommandData):

    PLUGIN_ID = 1053571
    PLUGIN_NAME = 'Vegas to C4D Markers'
    PLUGIN_INFO = 0
    PLUGIN_ICON = load_bitmap('res/icons/vegas-to-c4d-markers.png')
    PLUGIN_HELP = ''

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON,
            self.PLUGIN_HELP, self)

    def Execute(self, doc):

        #Input xml file location and check if it is an xml file (or if the file exists)
        file_loc = c4d.gui.InputDialog('XML File Location', '')
        if file_loc == '':
            print("Canceled")

        elif not file_loc.endswith(".xml"):
            gui.MessageDialog('The file you inputed does not end with ".xml"')

        else:
            try:
                tree = ET.parse(file_loc)
            except:
                gui.MessageDialog("It seems like the XML file location does not exist...")
            tree = ET.parse(file_loc)
            root = tree.getroot()

            print("Parsing...")
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
                marker_names = ''

                for markers in root.findall('project/children/sequence/marker'):
                    markers_found = markers_found + 1

                    #Parse frames in wich markers are
                    frame = markers.find('in').text
                    frame = str(frame)
                    frames = frames + frame + ','

                    #Assign names to the markers
                    marker_names = marker_names + str(markers_found) + ','


                frames = frames[:-1]
                marker_names = marker_names[:-1]
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
                    marker_names = marker_names.split(',')
                print("Done parsing!")

                # Start using all the info to create markers
                #Also check if the fps on the c4d project is the same as in the vegas project. If not asks if you would like to change it.
                fps = doc[c4d.DOCUMENT_FPS]
                if fps != float(sequence_rate):
                    change_rate = gui.QuestionDialog("The project framerate is not the same as the Vegas framerate! (" + sequence_rate + ") Would you like to change it? \n \n" + "Yes: Changes fps to " + sequence_rate + " and places all markers. \n" + "No: Cancels the operation.")
                    if change_rate == True:
                        sequence_rate = int(sequence_rate)
                        doc[c4d.DOCUMENT_FPS] = sequence_rate

                        #Open timeline window and start puttings marks
                        print("Placing markers...")
                        c4d.CallCommand(465001541, 465001541) # Timeline (Dope Sheet)...
                        for info, name in zip(frames, marker_names):
                            frame = float(info)
                            Time = c4d.BaseTime(frame,fps)
                            c4d.documents.AddMarker(doc, None, Time, name)
                        print("Done!")
                    else:
                        c4d.CallCommand(12373) # Project Settings...

                #If the fps on both projects match then continue normally
                else:

                    #Open timeline window and start puttings marks
                    print("Placing markers...")
                    c4d.CallCommand(465001541, 465001541) # Open Timeline (Dope Sheet)...
                    for info, name in zip(frames, marker_names):
                        frame = float(info)
                        Time = c4d.BaseTime(frame,fps)
                        c4d.documents.AddMarker(doc, None, Time, name)
                    print("Done!")

        return True


if __name__ == '__main__':
    VegastoC4DMarkers().Register()
