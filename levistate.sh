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
		if [ $? -ne 0 ]
		then
			echo "Unable to setup metroae container"
			return status
		fi
	else 
		
	    while read -r line; do declare $line; done < ~/.metroae
	    docker run -t -d --network host -v $mountPoint:/data registry.mv.nuagenetworks.net:5000/metroae 2> /dev/null
	    
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

upgradeDokcer() { 
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
	echo "help"
}

# main functionality

if [ $# -eq 0 ] || [ $1 == "help" ] || [ $1 == "-h" ] || [ $1 == "--h" ] 
then
	help
fi

if [ $1 == "pull" ] 
then
	pull
elif [ $1 == "setup" ]
then
	setup 
elif [ $1 == "stop" ]
then
	stop
elif [ $1 == "destroy" ]
then
	destroy
elif [ $1 == "upgrade" ] && [ $# -gt 2 ] 
then
	upgradeDocker
else
	dockerExec $@
fi
