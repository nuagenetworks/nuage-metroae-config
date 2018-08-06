#!/bin/bash
containerID=''
runningContainerID=''
imageID=''
maxContainerVersion='current'
confirmationMessage=''

getMaxContainerVersion() { 
	versions=`sudo docker images | grep registry.mv.nuagenetworks.net:5000/metroae | awk '{ print $2 }'`
	
	maxContainerVersion=''
	for version in $versions
	do
	        if [ -z $maxContainerVersion ]
	        then
	                maxContainerVersion=$version
	        fi
	
	        if [ $maxContainerVersion \< $version ]
	        then
	                maxContainerVersion=$version
	        fi
	done
	
}

getContainerID() { 
	#getMaxContainerVersion
	containerID=`sudo docker ps -a | grep metroae | grep $maxContainerVersion | awk '{ print $1}'`
}

getRunningContainerID() {
	#getMaxContainerVersion 
	runningContainerID=`sudo docker ps | grep metroae | grep $maxContainerVersion | awk '{ print $1}'`
}

getImageID() { 
	#getMaxContainerVersion 
	imageID=`sudo docker images | grep metroae | grep $maxContainerVersion | awk '{ print $3}'`
}



stop() {
	getContainerID
	
	if [ -z $containerID  ]
	then
		echo "No Container to stop"
		return 0
	fi
	
	sudo docker stop $containerID 
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

	getImageID
	
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
		getContainerID
		
		if [ -z $containerID ]
		then
			while read -r line; do declare $line; done < ~/.metroae
		    sudo docker run -t -d --network host -v $mountPoint:/data registry.mv.nuagenetworks.net:5000/metroae:$maxContainerVersion 2> /dev/null
		else 
			sudo docker start $containerID
		fi
	    
	    status=$?
		if [ $status -ne 0 ] 
		then
			echo "Unable to run the latest metroae docker image"
		fi
		
		return $status
	fi
}

deleteContainerID() {
	getContainerID
	if [ -z $containerID ]
	then
		echo "No container to remove" 
		return 0
	fi
	
	sudo docker rm $containerID 2> /dev/null
	
	if [ $? -ne 0 ]
	then
		echo "Remove of metroae container failed" 
		return 1
	fi
}

confirmAction() { 
	confirmation="init"
	while [ $confirmation != "yes" ] && [ $confirmation  != "no" ]
	do
		read -p $confirmationMessage confirmation
	done 
	
	if [ $confirmation == "yes" ]
	then
		return 0
	fi
	
	return 1
}

destroy() {
	echo $1
	if [ -z $1 ]
	then
		confirmation="init"
	else 
		confirmation=$1
	fi
	
	while [ $confirmation != "yes" ] && [ $confirmation  != "no" ]
	do
		read -p "Do you really want to destroy the container (yes/no): " confirmation
	done
 
	
	if [ $confirmation != "yes" ]
	then
		echo "Destroy Cancelled by user"
		return 1
	fi
	
	stop
	if [ $? -ne 0 ]
	then
		return 1
	fi
	
	deleteContainerID 
	if [ $? -ne 0 ]
	then
		return 1
	fi
	
	getImageID
	if [ -z $imageID ]
	then
		echo "No Image to remove"
		return 0
	fi
	
	sudo docker rmi $imageID  2> /dev/null
	
	if [ $? -ne 0 ]
	then
		echo "Remove of metroae image failed" 
		return 1
	fi
	
	return 0
}

pull() { 
	sudo docker pull registry.mv.nuagenetworks.net:5000/metroae:$maxContainerVersion 2> /dev/null
	
	status=$?
	if [ $status -ne 0 ] 
	then
		echo "Unable to pull the latest metroae docker image"
	fi
	
	return $status	
}

setup() {
	getImageID 
	
	if [ -z $imageID ]
	then 
		pull
	fi
	
	if [ $? -ne 0 ] 
	then
		return 1
	fi
	
	if [ -z $1 ]
	then
		read -p "Specify the full path to mount the docker volume: " path
	else 
		path=$1
	fi
	rm -f ~/.metroae
	echo mountPoint=$path >> ~/.metroae
	
	#stop and remove existing container if any
	getRunningContainerID 
	if [ ! -z $runningContainerID ]
	then
		stop
		deleteContainerID
	fi 
	
	run
	
	status=0
	if [ $? -ne 0 ]
	then
		return 1
	else 
		
		#download the templates and sample user data
		dockerExec upgrade-templates
		status=$?
	fi
	
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
	getRunningContainerID
	
	if [ -z $runningContainerID ]
	then
		run
		getRunningContainerID
	fi

	environment=""
	for env in `env`
	do
		environment="$environment -e $env"
	done

	sudo docker exec $environment $runningContainerID /usr/local/bin/python levistate.py $@
}

help() { 
	echo "usage: supported commands are help, pull, setup, stop, destroy, upgrade "
	echo "additionally supports commands that can be executed in the docker container" 
	
	dockerExec help
	
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
		if [ -z $2 ]
		then
			setup
		else 
			setup $2
			shift
		fi
		shift
		;;
		stop)
		stop
		shift
		;;
		destroy)
		if [ -z $2 ]
		then
			destroy
		else 
			destroy $2
			shift
		fi
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
