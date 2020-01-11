#! /usr/bin/env python3
# this script creates a docker container to run R interactively
import     time
import     csv
import     sys
import     os.path
import     os
import     subprocess
from       argparse import ArgumentParser
from       datetime import datetime, timedelta

# init globals
version='2.0'
msgErrPrefix='>>> Error (' + os.path.basename(__file__) +')'
msgInfoPrefix='>>> Info (' + os.path.basename(__file__) +')'
debugPrefix='>>> Debug (' + os.path.basename(__file__) +')'

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

def popen(cmd, sout=subprocess.PIPE, serr=subprocess.PIPE):
    process = subprocess.Popen(cmd, stdout=sout, stderr=serr, shell=True)
    status = process.wait()
    if status != 0:
        if serr != sys.stderr:
            pipe = process.stderr
            eMsg = pipe.readline()
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

    print( '\tDocker Options:' )
    print( '\t\tKeep container: ' + str(keepcontainer) )
    print( '\t\tProxy user: ' + defProxyUser )
    print( '\t\tDocker user: ' + dockeruser)
    print( '\t\tContainer name: ' + cname )
    print( '\t\tImage: ' + image )
    print( '\t\tVolume maps: ' + str(umv_list) )
    print( '\t\tWorking directory: ' + workdir )
    print( '\t\tR_LIBS_USER: ' + rlibsuser )
    print( '\tDocker run command: \n\t' + run_cmd)
    tbegin=time.asctime()
    print( '\tTime: ' + tbegin + "\n" )

defDockerImage = "uwgac/topmed-devel"
defMapVols = "/projects"
defgid = "2049"
defProxyUser = "topmed:2049"

# command line parser
parser = ArgumentParser( description = "Helper function to run R in docker" )
parser.add_argument( "-d", "--dockeruser",
                     help = "Docker user in container (userid[:groupid]) [defaut: local host user]" )
parser.add_argument( "-m", "--mapvols", default = defMapVols,
                     help = "local host volumes/folder(s) mapped into docker - comma delimited [default: " +
                     defMapVols + "]")
parser.add_argument( "-w", "--workdir",
                     help = "Work directory in docker[default: cwd]")
parser.add_argument( "--rlibsuser",
                     help = "R library (R_LIBS_USER) [default: cwd]" )
parser.add_argument( "-I", "--image", default = defDockerImage,
                     help = "docker image [default: " + defDockerImage + "]")
parser.add_argument( "-K", "--keepcontainer", action="store_true", default = False,
                     help = "Keep the container (it can be re-started) [default: False]" )
parser.add_argument( "-V", "--verbose", action="store_true", default = False,
                     help = "Turn on verbose output [default: False]" )
parser.add_argument( "-S", "--summary", action="store_true", default = False,
                     help = "Print summary prior to executing [default: False]" )
parser.add_argument( "--version", action="store_true", default = False,
                     help = "Print version of " + __file__ )

args = parser.parse_args()
# set result of arg parse_args
dockeruser = args.dockeruser
workdir = args.workdir
mapvols = args.mapvols
rlibsuser = args.rlibsuser
image = args.image
keepcontainer = args.keepcontainer
debug = args.verbose
summary = args.summary
# version
if args.version:
    print(__file__ + " version: " + version)
    sys.exit()
# process user (uid,gid) to set in docker
localUser = os.getenv("USER")
if dockeruser == None:
    maxid = 2147483647
    uid = os.getuid()
    if uid > maxid:
        pInfo("User " + localUser + " uid is too large; is too large; switching docker user to " + defProxyUser)
        dockeruser = defProxyUser
    else:
        gid = os.getgid()
        if gid > maxid:
            pInfo("User " + localUser + " gid is too large; using gid " + defgid)
            gid = defgid
        dockeruser = str(uid) + ":" + str(gid)
# working dir
if workdir == None:
    workdir = os.getenv("PWD")
# rlibsuser
if rlibsuser == None:
    rlibsuser = workdir

# build the run cmd
run_cmd = "docker run "
run_cmd += " -u " + dockeruser
# work dir
run_cmd += " -w " + workdir
# mapvols - add all directories to map
allmaps = mapvols + "," + workdir
if workdir != rlibsuser:
    allmaps += "," + rlibsuser
# mapvols - convert to list with -v option added
mv_list = allmaps.split(",")
umv_list = []
[umv_list.append(val) for val in mv_list if val not in umv_list]
vols = ["-v "+ mv+":"+mv for mv in umv_list]
vols_opt = " ".join(vols)
# mapvols - add to run cmd
run_cmd += " " + vols_opt
# environment - r libs user
run_cmd += " -e R_LIBS_USER=" + rlibsuser
# remove container
if not keepcontainer:
    run_cmd += " --rm"
# container name
cname = "R_" + os.getenv("USER")
run_cmd += " --name " + cname
# image and command
run_cmd += " -it " + image + " R"
# summarize and check for required params
if summary or debug:
    Summary("Summary of " + __file__)
    if summary:
        sys.exit()
# check if container exists; if so start it
c_cmd = 'docker ps -a --filter "name=^"' + cname + ' --format "{{.Names}}"'
o_cmd = popen(c_cmd)
c_exists = False
if len(o_cmd) != 0:
    c_exists = True
if c_exists:
    pInfo("Starting container " + cname)
    run_cmd = "docker start -a -i " + cname
    pDebug("Docker cmd: \n" + run_cmd)
    popen(run_cmd, sys.stdout, sys.stderr)
    if not keepcontainer:
        run_cmd = "docker rm -f " + cname
        pDebug("Docker cmd: \n" + run_cmd)
        popen(run_cmd, sys.stdout, sys.stderr)
else:
    pInfo("Running docker ...")
    pDebug("Docker cmd: \n" + run_cmd)
    popen(run_cmd, sys.stdout, sys.stderr)
