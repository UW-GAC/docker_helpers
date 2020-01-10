#! /usr/bin/env python3
# this script creates a docker container to run Rstudio server in the background
# so that a local browser can execute Rstudio
import     time
import     csv
import     sys
import     os.path
import     os
import     subprocess
from       argparse import ArgumentParser
from       datetime import datetime, timedelta
import     socket

# init globals
version='2.0'
msgErrPrefix='>>> Error (' + os.path.basename(__file__) +')'
msgInfoPrefix='>>> Info (' + os.path.basename(__file__) +')'
debugPrefix='>>> Debug (' + os.path.basename(__file__) +')'

ipinfo = {"host": None, "addr": None}
# def functions
def pInfo(msg):
    tmsg=time.asctime()
    print(msgInfoPrefix+tmsg+": "+msg)

def pError(msg):
    tmsg=time.asctime()
    print(msgErrPrefix+tmsg+": "+msg)

def pDebug(msg):
    if debug:
        tmsg=time.asctime()
        print(debugPrefix+tmsg+": "+msg)
def getIP():
    ipinfo["host"] = socket.gethostname()
    ipinfo["addr"] = socket.gethostbyname(ipinfo["host"])
    return ipinfo

def popen(cmd, sout=subprocess.PIPE, serr=subprocess.PIPE):
    process = subprocess.Popen(cmd, stdout=sout, stderr=serr, shell=True)
    status = process.wait()
    if status != 0:
        if serr != sys.stderr:
            pipe = process.stderr
            eMsg = pipe.readline()
            eMsg = bytes(eMsg).decode()
        else:
            eMsg = "See terminal"
        pError("Error executing cmd: \n\t" + cmd)
        pError("Error status: " + str(status) + " - " + eMsg)
        sys.exit(2)
    if sout != sys.stdout:
        pipe = process.stdout
        sub_out = pipe.readline()
        # compatibility p2/p3: byte seq or string converts to string
        sub_out = bytes(sub_out).decode()
    else:
        sub_out = ""
    return sub_out

def Summary(hdr):
    print(hdr)
    print( '\tVersion: ' + version)

    print( '\tDocker:' )
    print( '\t\tContainer name: ' + namecontainer )
    print( '\t\tImage: ' + image )
    print( '\t\tRstudio server port: ' + dockerPort )
    print( '\t\tLocal host port: ' + localport )
    print( '\t\tLocal host IP: ' + ipinfo["addr"] )
    print( '\t\tLocal host name: ' + ipinfo["host"] )
    print( '\t\tMapped volumes: ' + mapvols )
    print( '\tDocker run command: \n\t' + run_cmd )
    tbegin=time.asctime()
    print( '\tTime: ' + tbegin + "\n" )

defDockerImage = "uwgac/tm-rstudio-devel:latest"
defMapVols = "/projects"
defCName = "rstudio_docker"
defLocalPort = "8686"
dockerPort = "8787"

# command line parser
parser = ArgumentParser( description = "Helper function to run Rstudio server in docker" )
parser.add_argument( "-m", "--mapvols", default = defMapVols,
                     help = "local host volumes/folder(s) mapped into docker - e.g., '/projects,/home' [default: " +
                     defMapVols + "]")
parser.add_argument( "-I", "--image", default = defDockerImage,
                     help = "docker image to initiate pipeline execution [default: " + defDockerImage + "]")
parser.add_argument( "-l", "--localport", default = defLocalPort,
                     help = "Local computer's port mapped to Rstudio in docker [default: " + defLocalPort + "]")
parser.add_argument( "-n","--namecontainer", default = defCName,
                     help = "name of container [default: " + defCName + "]" )
parser.add_argument( "-V", "--verbose", action="store_true", default = False,
                     help = "Turn on verbose output [default: False]" )
parser.add_argument( "-S", "--summary", action="store_true", default = False,
                     help = "Print summary prior to executing [default: False]" )
parser.add_argument( "--version", action="store_true", default = False,
                     help = "Print version of " + __file__ )

args = parser.parse_args()
# set result of arg parse_args
mapvols = args.mapvols
image = args.image
localport = args.localport
image = args.image
namecontainer = args.namecontainer
verbose = args.verbose
debug = verbose
summary = args.summary
# version
if args.version:
    print(__file__ + " version: " + version)
    sys.exit()

# get ip info
ipinfo = getIP()

# build the docker run command to create and start the container
run_cmd = "docker run -d -t "
run_cmd += "--name " + namecontainer
# mapvols - make each mapvol m1:m1
mv_list = mapvols.split(",")
vols = ["-v "+ mv+":"+mv for mv in mv_list]
vols_opt = " ".join(vols)
run_cmd += " " + vols_opt
# port
run_cmd += " -p " + ipinfo["addr"] + ":" + localport + ":" + dockerPort
# image
run_cmd += " " + image

# summarize and check for required params
if summary or verbose:
    Summary("Summary of " + __file__)
    if summary:
        sys.exit()
pInfo("Running docker ...")
pDebug("Docker cmd: \n" + run_cmd)
sub_out = popen(run_cmd)
pInfo("Status return: " + sub_out)
