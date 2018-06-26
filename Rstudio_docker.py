#! /usr/bin/env python
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

# init globals
version='1.0'
msgErrPrefix='>>> Error (' + os.path.basename(__file__) +')'
msgInfoPrefix='>>> Info (' + os.path.basename(__file__) +')'
debugPrefix='>>> Debug (' + os.path.basename(__file__) +')'

# def functions
def pInfo(msg):
    tmsg=time.asctime()
    print msgInfoPrefix+tmsg+": "+msg

def pError(msg):
    tmsg=time.asctime()
    print msgErrPrefix+tmsg+": "+msg

def pDebug(msg):
    if debug:
        tmsg=time.asctime()
        print debugPrefix+tmsg+": "+msg

def Summary(hdr):
    print(hdr)
    print( '\tVersion: ' + version)

    print( '\tDocker:' )
    print( '\t\tContainer name: ' + name )
    print( '\t\tImage: ' + image )
    print( '\t\tRstudio server port: ' + dockerport )
    print( '\t\tLocal host port: ' + port )
    print( '\t\tLocal host IP: ' + ip )
    print( '\t\tBind-mount local dir: ' + localdir )
    print( '\t\tBind-mount docker dir: ' + dockerdir )
    tbegin=time.asctime()
    print( '\tTime: ' + tbegin + "\n" )

defDockerImage = "uwgac/topmed-rstudio"
defName = "rstudio"
defLocalPort = "8787"
defDockerDir = "/home/rstudio"
defHostIP = "localhost"
defDockerPort = "8787"
defRunCmd = "run"
defKillCmd = "kill"

# command line parser
parser = ArgumentParser( description = "Helper function to run Rstudio server in docker" )
parser.add_argument( "-l", "--localdir",
                     help = "full path of local work directory [default: current working directory]" )
parser.add_argument( "-d", "--dockerdir", default = defDockerDir,
                     help = "full path of docker work directory [default: " + defDockerDir +"]" )
parser.add_argument( "-I", "--image", default = defDockerImage,
                     help = "docker image to initiate pipeline execution [default: " + defDockerImage + "]")
parser.add_argument( "-p", "--port", default = defLocalPort,
                     help = "Local computer's port mapped to Rstudio in docker [default: " + defLocalPort + "]")
parser.add_argument( "-i", "--ip", default = defHostIP,
                     help = "Local computer's IP mapped to docker's IP [default: " + defHostIP + "]")
parser.add_argument( "-D", "--dockerport", default = defDockerPort,
                     help = "Rstudio server's port in docker [default: " + defDockerPort + "]")
parser.add_argument( "-n","--name", default = defName,
                     help = "name of container [default: " + defName + "]" )
parser.add_argument( "-C","--command", default = defRunCmd,
                     help = "Docker command (run or kill) [default: " + defRunCmd + "]" )
parser.add_argument( "-V", "--verbose", action="store_true", default = False,
                     help = "Turn on verbose output [default: False]" )
parser.add_argument( "-S", "--summary", action="store_true", default = False,
                     help = "Print summary prior to executing [default: False]" )
parser.add_argument( "--version", action="store_true", default = False,
                     help = "Print version of " + __file__ )

args = parser.parse_args()
# set result of arg parse_args
localdir = args.localdir
dockerdir = args.dockerdir
dockerport = args.dockerport
image = args.image
port = args.port
ip = args.ip
name = args.name
verbose = args.verbose
summary = args.summary
command = args.command
# version
if args.version:
    print(__file__ + " version: " + version)
    sys.exit()

# check localdir; if not passed using cwd
if localdir == None:
    localdir = os.getenv('PWD')

# check local ip
if ip == defHostIP:
    ip = "127.0.0.1"

# summarize and check for required params
if summary or verbose:
    Summary("Summary of " + __file__)
    if summary:
        sys.exit()
if command == defRunCmd:
    print("=====================================================================")
    pInfo("\n\tRunning Rstudio server in docker image: " + image)
    print("=====================================================================")
    dockerCMD = "docker run -d -t " + " --name " + name + \
                " -v " + localdir + ":" + dockerdir + \
                " -w " + dockerdir + \
                " -p " + ip + ":" + port + ":" + dockerport + \
                " " + image
    if verbose:
        pInfo("Docker cmd:\n\t" + dockerCMD)
    process = subprocess.Popen(dockerCMD, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    status = process.wait()
    if status:
        pError("Docker run command failed:\n\t" + str(status) )
        sys.exit(2)
elif command == defKillCmd:
    print("=====================================================================")
    pInfo("\n\tKilling the docker container running Rstudio: " + name)
    print("=====================================================================")
    dockerCMD = "docker stop " + name
    if verbose:
        pInfo("Docker cmd:\n\t" + dockerCMD)
    process = subprocess.Popen(dockerCMD, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    status = process.wait()
    if status:
        pError("Docker stop command failed:\n\t" + str(status) )
        sys.exit(2)
    dockerCMD = "docker rm " + name
    if verbose:
        pInfo("Docker cmd:\n\t" + dockerCMD)
    process = subprocess.Popen(dockerCMD, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    status = process.wait()
    if status:
        pError("Docker rm command failed:\n\t" + str(status) )
        sys.exit(2)

else:
    pError("Invalid command " + command)
    sys.exit(2)

if verbose:
    pInfo("Python script " + __file__ + " completed without errors")
