#! /usr/bin/env python
# this script runs a topmed docker image so that users can interactively run the
# analysis pipeline.
import     time
import     csv
import     sys
import     os.path
import     os
import     subprocess
import     getpass
from       argparse import ArgumentParser
from       datetime import datetime, timedelta

# init globals
version='1.0'
msgErrPrefix='>>> Error (' + os.path.basename(__file__) +')'
msgInfoPrefix='>>> Info (' + os.path.basename(__file__) +')'
debugPrefix='>>> Debug (' + os.path.basename(__file__) +')'

# def functions
def add2parameters(inparams,inopt,inoptVal):
    params=inparams
    # if inopt not already defined add to params
    if inopt not in params:
        params=params + " " + inopt
        if inoptVal is not None:
            params=params + " " + inoptVal
    return params


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
    print( '\tVersion: ' + version )
    print( '\tLocal project data root dir: ' + dataroot )
    print( '\tLocal aws security file: ' + localsecurity )

    print( '\tDocker:' )
    print( '\t\tImage: ' + image )
    print( '\t\tWork dir: ' + workdir )
    print( '\t\tProject root dir: ' + dockerroot )
    print( '\t\tDocker aws security file: ' + dockersecurity )
    print( '\t\tUse existing container: ' + str(existingcontainer) )
    print( '\t\tKeep container: ' + str(keepcontainer) )
    print( '\t\tContainer name: ' + name )
    print( '\t\tCreate container opts: ' + createopts )
    tbegin=time.asctime()
    print( '\tTime: ' + tbegin + "\n" )

defCreateOpts = "-it"
defDockerSecurity = "/root/.aws"
defLocalSecurity = "~/.aws"
defDockerImage = "uwgac/topmed-master"
defName = "analysis_pipeline"

# command line parser
parser = ArgumentParser( description = "Helper function to run a topmed docker image interactively for running the analysis pipeline" )
parser.add_argument( "-w", "--workdir",
                     help = "working directory (full path) [default: current working directory]" )
parser.add_argument( "-d", "--dataroot", default = None,
                     help = "topmed project data root in local computer [default: root dir of working directory]" )
parser.add_argument( "-D", "--dockerroot", default = None,
                     help = "topmed project data root in docker [default: root dir of working directory]" )
parser.add_argument( "-i", "--image", default = defDockerImage,
                     help = "docker image to initiate pipeline execution [default: " + defDockerImage + "]")
parser.add_argument( "-c", "--createopts", default = defCreateOpts,
                     help = "docker create container options [default: " + defCreateOpts + "]")
parser.add_argument( "--localsecurity", default = defLocalSecurity,
                     help = "aws credentials file to map to docker [default: ]" + defLocalSecurity + "]" )
parser.add_argument( "--dockersecurity", default = defDockerSecurity,
                     help = "security file location in docker [default: " + defDockerSecurity + "]" )
parser.add_argument( "-e","--existingcontainer", action="store_true", default = False,
                     help = "start an existing container [default: False]" )
parser.add_argument( "-n","--name",
                     help = "name of container [default: analysis_pipeline_<username>]" )
parser.add_argument( "-k", "--keepcontainer", action="store_true", default = False,
                     help = "Keep the container and do not stop it [default: False]" )
parser.add_argument( "-V", "--verbose", action="store_true", default = False,
                     help = "Turn on verbose output [default: False]" )
parser.add_argument( "-S", "--summary", action="store_true", default = False,
                     help = "Print summary prior to executing [default: False]" )
parser.add_argument( "--version", action="store_true", default = False,
                     help = "Print version of " + __file__ )

args = parser.parse_args()
# set result of arg parse_args
workdir = args.workdir
dataroot = args.dataroot
dockerroot = args.dockerroot
image = args.image
createopts = args.createopts
localsecurity = args.localsecurity
dockersecurity = args.dockersecurity
existingcontainer = args.existingcontainer
name = args.name
keepcontainer = args.keepcontainer
verbose = args.verbose
summary = args.summary
# set container name
if name == None:
    user = getpass.getuser()
    name = defName + "_" + user
# version
if args.version:
    print(__file__ + " version: " + version)
    sys.exit()

if not keepcontainer:
    createopts = createopts + " --rm"
# if not using existing container, then process all the args
if not existingcontainer:
    # check workdir; if not passed using cwd
    if workdir == None:
        workdir = os.getenv('PWD')
    # check if local data root is passed; else use root of cwd
    if dataroot == None:
        dl = workdir.split("/")
        dataroot = "/" + dl[1]
    # check if docker root is passed; else use local dataroot
    if dockerroot == None:
        dockerroot = dataroot
else:
    workdir = "N/A"
    dataroot = "N/A"
    dockerroot = "N/A"
    createopts = "N/A"
    localsecurity = "N/A"
    dockersecurity = "N/A"
# summarize and check for required params
if summary or verbose:
    Summary("Summary of " + __file__)
    if summary:
        sys.exit()
print("=====================================================================")
pInfo("\n\tSending analysis to docker image: " + image)
print("=====================================================================")
# create container and copy security
if not existingcontainer:
    dsFile = dockersecurity + "/" + os.path.basename(localsecurity)
    createCMD = "docker create " + createopts + " --name " + name + \
                " -v " + dataroot + ":" + dockerroot + \
                " -v " + localsecurity + ":" + dockersecurity + \
                " -w " + workdir + \
                " " + image
    if verbose:
        pInfo("Docker create container cmd:\n" + createCMD)
    process = subprocess.Popen(createCMD, shell=True, stdout=subprocess.PIPE)
    status = process.wait()
    pipe = process.stdout
    msg = pipe.readline()
    if status:
        pError("Docker create command failed: " + msg )
        sys.exit(2)

# just use existing container
else:
    if verbose:
        pInfo("Use existing container named: " + name)

# start the container
startCMD = "docker start -i " + name
if verbose:
    pInfo("Docker start cmd: " + startCMD)
process = subprocess.Popen(startCMD, stdout=sys.stdout, stderr=sys.stderr, shell=True)
status = process.wait()
if status:
    pError("Docker start command failed:\n\t" + str(status) )
    sys.exit(2)

if verbose:
    pInfo("Python script " + __file__ + " completed without errors")
