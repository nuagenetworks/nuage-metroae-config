#!/bin/bash

getContainerID() { 
	containerId=`docker ps -a | grep metroae | awk '{ print $1}'`
	
	echo $containerId 
}

getRunningContainerID() { 
	containerId=`docker ps | grep metroae | awk '{ print $1}'`
	
	echo $containerId
}

getImageID() { 
	imageID=`docker images | grep metroae | awk '{ print $3}'`
	
	echo $imageID
}

stop() {
	containerID=$(getContainerID)
	docker stop $containerID 2> /dev/null
	status=$?
	if [ $status -ne 0 ]
	then
		echo "Stopping metroae docker container failed"
	else 
		echo "Container successfully stopped" 
	fi
	
	return $status
}

run() { 

	imageID=$(getImageID)
	
	if [ -z $imageID ] 
	then
		setup
		status=$?
		if [ $status -ne 0 ]
		then
			echo "Unable to setup metroae container"
			return $status 
		fi
	else 
		containerID=$(getContainerID)
		
		if [ -z $containerID ]
		then
			while read -r line; do declare $line; done < ~/.metroae
		    docker run -t -d --network host -v $mountPoint:/data registry.mv.nuagenetworks.net:5000/metroae 2> /dev/null
		else 
			docker start $containerID
		fi
	    
	    status=$?
		if [ $status -ne 0 ] 
		then
			echo "Unable to run the latest metroae docker image"
		fi
		
		return $status
	fi
}

destroy() { 
	stop
	if [ $? -ne 0 ]
	then
		return 1
	fi
	
	containerID=$(getContainerID)
	docker rm $containerID 2> /dev/null
	
	if [ $? -ne 0 ]
	then
		echo "Remove of metroae container failed" 
		return 1
	fi
	
	imageID=$(getImageID)
	echo $imageID
	docker rmi $imageID  2> /dev/null
	
	if [ $? -ne 0 ]
	then
		echo "Remove of metroae image failed" 
		return 1
	fi
	
	return 0
}

pull() { 
	docker pull registry.mv.nuagenetworks.net:5000/metroae:latest 2> /dev/null
	
	status=$?
	if [ $status -ne 0 ] 
	then
		echo "Unable to pull the latest metroae docker image"
	fi
	
	return $status	
}

setup() { 
	pull
	
	if [ $? -ne 0 ] 
	then
		return 1
	fi
	
	read -p "Specify the full path to mount the docker volume: " path
	rm -f ~/.metroae
	echo mountPoint=$path >> ~/.metroae
	
	run
	status=$?
	
	return $status
}

upgradeDocker() { 
	destroy 
	if [ $? -ne 0 ]
	then
		return 1
	fi
	
	pull
	run	
}

dockerExec() { 
	containerID=$(getRunningContainerID)
	
	if [ -z $containerID ]
	then
		run
		containerID=$(getRunningContainerID)
	fi
	
	docker exec -e env $containerID python levistate.py $@
}

help() { 
	echo "usage: supported commands are help, pull, setup, stop, destroy, upgrade "
	echo "additionally supports commands that can be executed in the docker container" 
	
}

# main functionality

if [ $# -eq 0 ] 
then
	help
fi


POSITIONAL=()
exec=false
while [ $# -gt 0 ]
do
key=$1

	case $key in
		help)
		help
		shift
		;;
		pull)
		pull
		shift
		;;
		setup)
		setup
		shift
		;;
		stop)
		stop
		shift
		;;
		destroy)
		destroy
		shift
		;;
		upgrade)
		if [ $2 == "engine" ] || [ $2 == "Engine" ]
		then
			upgradeDocker 
		fi
		shift
		shift
		;;
		*)
		POSITIONAL+=($1)
		exec=true
		shift
		;;
	esac
done

if ($exec == true)
then
	dockerExec $POSITIONAL
fi