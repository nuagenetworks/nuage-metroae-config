#!/bin/bash
containerID=''
runningContainerID=''
imageID=''
maxContainerVersion='current'
confirmationMessage=''
metroAEImage='registry.mv.nuagenetworks.net:5000/metroae'

checkDocker() {
	docker --version > /dev/null 2> /dev/null

	if [ $? -ne 0 ]
	then
		echo "MetroAE container requires Docker.  Please install at https://docs.docker.com"
		exit 1
	fi
}

getMaxContainerVersion() {
	versions=`sudo docker images | grep $metroAEImage | awk '{ print $2 }'`

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

	echo "Stopping MetroAE container..."

	sudo docker stop $containerID
	status=$?
	if [ $status -ne 0 ]
	then
		echo "Stopping MetroAE docker container failed"
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
			echo "Unable to setup MetroAE container"
			return $status
		fi
	else
		getContainerID

		if [ -z $containerID ]
		then
			while read -r line; do declare $line; done < ~/.metroae
		    sudo docker run -t -d --network host -v $LEVISTATE_MOUNT_POINT:/data $metroAEImage:$maxContainerVersion 2> /dev/null
		else
			sudo docker start $containerID
		fi

	    status=$?
		if [ $status -ne 0 ]
		then
			echo "Unable to run the latest MetroAE docker image"
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
		echo "Remove of MetroAE container failed"
		return 1
	fi
}

destroy() {
	echo $1
	if [ -z $1 ]
	then
		confirmation="init"
	else
		confirmation=$1
	fi

	while [ $confirmation != "yes" ] && [ $confirmation  != "no" ] && [ $confirmation  != "y" ] && [ $confirmation != "n" ]
	do
		read -p "Do you really want to destroy the MetroAE container (yes/no): " confirmation
	done

	if [ $confirmation != "yes" ] && [ $confirmation != "y" ]
	then
		echo "Destroy cancelled by user"
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
		echo "No image to remove"
		return 0
	fi

	echo "Destroying MetroAE container..."

	sudo docker rmi $imageID  2> /dev/null

	if [ $? -ne 0 ]
	then
		echo "Remove of MetroAE image failed"
		return 1
	fi

	return 0
}

pull() {
	echo "Retrieving MetroAE container..."

	sudo docker pull $metroAEImage:$maxContainerVersion 2> /dev/null

	status=$?
	if [ $status -ne 0 ]
	then
		echo "Unable to pull the latest MetroAE docker image"
	fi

	return $status
}

setup() {
	echo "Setup MetroAE container..."

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
		read -p "Specify the full path to store user data on the host system: " path
	else
		path=$1
	fi

	echo LEVISTATE_MOUNT_POINT=$path >> ~/.metroae

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
	echo "usage: supported commands are help, version, pull, setup, stop, destroy, upgrade-engine "
	echo "additionally supports commands that can be executed in the docker container"

	dockerExec help

}

showVersion() {
	dockerExec version
}

# main functionality

checkDocker

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
		version)
		showVersion
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
		upgrade-engine)
		upgradeDocker
		shift
		;;
		*)
		POSITIONAL+=("$1")
		exec=true
		shift
		;;
	esac
done

if ($exec == true)
then
	dockerExec ${POSITIONAL[@]}
fi
