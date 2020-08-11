## Configuration Engine Installation


MetroAE Configuration engine is provided as a Docker container. The installation of the container is handled via an install and management script. Along with the configuration container we also require some additional data.

On a host where the configuration engine will be installed the following artifacts will be installed.
1. Docker container for configuration
2. Collection of configuration Templates
3. VSD API Specification


#### System Requirements
* Operating System: RHEL/Centos 7.4+
* Docker: Docker Engine 1.13.1+
* Network Access: Internal and Public
* Storage: At least 800MB

##### Operating system
The primary requirement for the configuration container is Docker Engine, however the installation, container operation and functionality is only tested on RHEL/Centos 7.4. Many other operating systems will support Docker Engine, however support for these is not currently provided and would be considered experimental only. A manual set of installation steps is provided for these cases.  

##### Docker Engine
The configuration engine is packaged into a Docker container. This ensures that all package and library requirements are self-contained with no other host dependencies. To support this, Docker Engine must be installed on the host. The configuration container requirements, however, are quite minimal. Primarily, the Docker container mounts a local path on the host as a volume while ensuring that any templates and user data are maintained only on the host. The user never needs to interact directly with the container.  

##### Network Access
Currently the configuration container is hosted in an internal Docker registry and the public network as a secondary option, while the Templates and API Spec are hosted only publicly. The install script manages the location of these resources. The user does not need any further information. However, without public network access the installation will fail to complete.

##### Storage
The configuration container along with the templates requires 800MB of local disk space. Note that the container itself is ~750MB, thus it is recommended that during install a good network connection is available.

##### User Privileges

The user must have elevated privileges on the host system.


### Installing via installation script


1. Install Docker Engine

    ```
    [metroae-user@metroae-host]# yum install docker -y
    Loaded plugins: search-disabled-repos
    Resolving Dependencies
    --> Running transaction check
    ---> Package docker.x86_64 2:1.13.1-88.07f3374.el7 will be installed
    --> Finished Dependency Resolution
    
    Dependencies Resolved
    
    ======================================================================================================================================================================================
     Package                           Arch                              Version                                                Repository                                           Size
    ======================================================================================================================================================================================
    Installing:
     docker                            x86_64                            2:1.13.1-88.git07f3374.el7                             rhel-7-server-extra-rpms                             16 M
    
    Transaction Summary
    ======================================================================================================================================================================================
    Install  1 Package
    
    Total download size: 16 M
    Installed size: 57 M
    Downloading packages:
    docker-1.13.1-88.git07f3374.el7.x86_64.rpm                                                                                                                     |  16 MB  00:00:03
    Running transaction check
    Running transaction test
    Transaction test succeeded
    Running transaction
      Installing : 2:docker-1.13.1-88.git07f3374.el7.x86_64                                                                                                                           1/1
      Verifying  : 2:docker-1.13.1-88.git07f3374.el7.x86_64                                                                                                                           1/1
    
    Installed:
      docker.x86_64 2:1.13.1-88.git07f3374.el7
    
    Complete!
    ```


2. Enable and Start Docker Engine Service

    ```
    [metroae-user@metroae-host]# systemctl enable docker
    Created symlink from /etc/systemd/system/multi-user.target.wants/docker.service to /usr/lib/systemd/system/docker.service.
    [metroae-user@metroae-host]# systemctl start docker
    ```
    
    Verify that the service is running.
    
    ```
    [root@metroae-host ~]# systemctl status docker
    ● docker.service - Docker Application Container Engine
       Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
       Active: active (running) since Tue 2019-07-09 16:41:14 UTC; 3min 41s ago
         Docs: http://docs.docker.com
     Main PID: 3206 (dockerd-current)
       CGroup: /system.slice/docker.service
               ├─3206 /usr/bin/dockerd-current --add-runtime docker-runc=/usr/libexec/docker/docker-runc-current --default-runtime=docker-runc --exec-opt native.cgroupdriver=systemd --use...
               └─3220 /usr/bin/docker-containerd-current -l unix:///var/run/docker/libcontainerd/docker-containerd.sock --metrics-interval=0 --start-timeout 2m --state-dir /var/run/docker...
    ```
    
    We can check wether docker is running also via running a sample docker command. ie. "docker version"
    
    ```
    [root@metroae-host ~]# docker --version
    Docker version 1.13.1, build 07f3374/1.13.1
    ```

3. Add the user to the wheel and docker groups. In this case the user is "caso"

    ```
    [root@metroae-host ~]# gpasswd -a caso wheel
    Adding user caso to group wheel
    [root@metroae-host ~]# gpasswd -a caso docker
    Adding user caso to group docker
    ```

4. Move or Copy the "metroae" script to /usr/bin and set permissions correctly to make the script executable.

    ```
    [root@metroae-host ~]# mv metroae /usr/bin
    [root@metroae-host ~]# chmod 755 /usr/bin/metroae
    [root@metroae-host ~]# ls -la /usr/bin | grep metroae
    -rwxr-xr-x.  1 root root      64264 Jul  9 17:13 metroae
    ```

    Note that this is a requirement for the initial release, the GA release will use an rpm install.

5. Switch to the user that will operate "metroae config" and check the script is running ok. In this case per step 3 its the "caso" user.

    ```
    [caso@metroae-host ~]$ metroae help
    Nuage Networks Metro Automation Engine (MetroAE) Version: v3.3.0
    
    MetroAE usage:
    
    metroae config                                            Configure VSD
    metroae config help                                       Displays the help text for levistate
    metroae config version                                    Displays the current levistate version
    metroae config engine update                              Update levistate to the latest version
    metroae config <positional args>                          Execute levistate inside the container
    metroae container                                         Manage the MetroAE container
    metroae container pull                                    Pull a new MetroAE image from the registry
    metroae container setup                                   Setup the mertroae container
    metroae container start                                   Start the mertroae container
    metroae container stop                                    Stop the mertroae container
    metroae container status                                  Display the status of the mertroae container
    metroae container destroy                                 Destroy the mertroae container
    metroae container update                                  Update the mertroae container to the latest version
    metroae container ssh copyid                              Copy the container ssh public key to a host
    
    Additional menu help is available by adding 'help' to the command line,
    e.g. 'metroae container help'
    ```

    Note if previously the user was not added to wheel and docker there would be various permissions issues seen here.

6. Setup the container using the metroae script.

    We are going to pull the image and setup the metro container in one command below. During the install we will be prompted for a location for the container data directory. This is the location where our user data, templates and VSD API specs will be installed and created and a volume mount for the container will be created. However this can occur orthogonally via "pull" and "setup" running at separate times which can be useful depending on available network bandwidth.
    ```
    [caso@metroae-host ~]$ metroae container help
    Nuage Networks Metro Automation Engine (MetroAE) Version: v3.3.0
    
    MetroAE container usage:
    
    metroae container                                         Manage the MetroAE container
    metroae container pull                                    Pull a new MetroAE image from the registry
    metroae container setup                                   Setup the mertroae container
    metroae container start                                   Start the mertroae container
    metroae container stop                                    Stop the mertroae container
    metroae container status                                  Display the status of the mertroae container
    metroae container destroy                                 Destroy the mertroae container
    metroae container update                                  Update the mertroae container to the latest version
    metroae container ssh copyid                              Copy the container ssh public key to a host
    ```

    We will use "metroae container setup".
    ```
    [caso@metroae-host ~]$ metroae container setup
    
    >>> Checking docker version
    
    >>> Setup MetroAE container
    
    Elevated privileges are required for setup. During setup, we may prompt you
    for the sudo password.
    
    >>> Pulling the MetroAE container image from the repository
    
    
    >>> Pulling the MetroAE container image from Nokia registry
    
    Trying to pull repository registry.mv.nuagenetworks.net:5000/metroae ...
    softlaunch: Pulling from registry.mv.nuagenetworks.net:5000/metroae
    9a598663ae73: Pulling fs layer
    b827d31025a3: Pulling fs layer
    97bbe95d2d2f: Pulling fs layer
    37ac171a5273: Pulling fs layer
    d1708ac1780b: Pulling fs layer
    3d34009f3311: Pulling fs layer
    8a68a0cc2542: Pulling fs layer
    3a8eefbe7d69: Pulling fs layer
    0e16004b6d62: Pulling fs layer
    15c94733df9e: Pulling fs layer
    57ed50c82d62: Pulling fs layer
    685cde86f35f: Pulling fs layer
    f59cd4a686f5: Pulling fs layer
    8903b9128b3d: Pulling fs layer
    8f0aca9b1856: Pulling fs layer
    700a872398e6: Pulling fs layer
    6dfae24ca868: Pulling fs layer
    df6b49f8cc7d: Pulling fs layer
    4e368f70cd0b: Pulling fs layer
    37ac171a5273: Waiting
    d1708ac1780b: Waiting
    3d34009f3311: Waiting
    8a68a0cc2542: Waiting
    3a8eefbe7d69: Waiting
    0e16004b6d62: Waiting
    15c94733df9e: Waiting
    57ed50c82d62: Waiting
    685cde86f35f: Waiting
    f59cd4a686f5: Waiting
    8903b9128b3d: Waiting
    8f0aca9b1856: Waiting
    700a872398e6: Waiting
    6dfae24ca868: Waiting
    df6b49f8cc7d: Waiting
    4e368f70cd0b: Waiting
    b827d31025a3: Verifying Checksum
    b827d31025a3: Download complete
    37ac171a5273: Verifying Checksum
    37ac171a5273: Download complete
    9a598663ae73: Verifying Checksum
    9a598663ae73: Download complete
    97bbe95d2d2f: Verifying Checksum
    97bbe95d2d2f: Download complete
    8a68a0cc2542: Verifying Checksum
    8a68a0cc2542: Download complete
    d1708ac1780b: Verifying Checksum
    d1708ac1780b: Download complete
    3a8eefbe7d69: Verifying Checksum
    3a8eefbe7d69: Download complete
    15c94733df9e: Verifying Checksum
    15c94733df9e: Download complete
    57ed50c82d62: Verifying Checksum
    57ed50c82d62: Download complete
    9a598663ae73: Pull complete
    b827d31025a3: Pull complete
    3d34009f3311: Verifying Checksum
    3d34009f3311: Download complete
    f59cd4a686f5: Verifying Checksum
    f59cd4a686f5: Download complete
    8903b9128b3d: Verifying Checksum
    8903b9128b3d: Download complete
    8f0aca9b1856: Verifying Checksum
    8f0aca9b1856: Download complete
    685cde86f35f: Verifying Checksum
    685cde86f35f: Download complete
    700a872398e6: Verifying Checksum
    700a872398e6: Download complete
    0e16004b6d62: Verifying Checksum
    0e16004b6d62: Download complete
    df6b49f8cc7d: Verifying Checksum
    df6b49f8cc7d: Download complete
    4e368f70cd0b: Verifying Checksum
    4e368f70cd0b: Download complete
    6dfae24ca868: Verifying Checksum
    6dfae24ca868: Download complete
    97bbe95d2d2f: Pull complete
    37ac171a5273: Pull complete
    d1708ac1780b: Pull complete
    3d34009f3311: Pull complete
    8a68a0cc2542: Pull complete
    3a8eefbe7d69: Pull complete
    0e16004b6d62: Pull complete
    15c94733df9e: Pull complete
    57ed50c82d62: Pull complete
    685cde86f35f: Pull complete
    f59cd4a686f5: Pull complete
    8903b9128b3d: Pull complete
    8f0aca9b1856: Pull complete
    700a872398e6: Pull complete
    6dfae24ca868: Pull complete
    df6b49f8cc7d: Pull complete
    4e368f70cd0b: Pull complete
    Digest: sha256:422fcd0ffe7b02c910c2824c4a074575c5fb2d5aed8d2fca8d3b595765856ba7
    Status: Downloaded newer image for registry.mv.nuagenetworks.net:5000/metroae:softlaunch
    Successfully Pulled the MetroAE container image from Docker registry
    
    >>> Setup container for MetroAE config only
    
    Data directory configuration
    
    The MetroAE container needs access to your user data. It gets access by internally
    mounting a directory from the host. We refer to this as the 'data directory'.
    The data directory is where you will have deployments, templates, documentation,
    and other useful files.
    
    Please specify the full path to the data directory on the Docker host. Setup will
    make sure that the path ends with 'metroae_data'. If the path you specify does
    not end with 'metroae_data', setup willl create it.
    
    Data directory path: /home/caso/
    
    Checking path: Data directory path
    >>> Data directory path set to: /home/caso/metroae_data
    
    
    >>> Starting the MetroAE container
    
    574c7314aa7ee61ab6d29effa76dc233409ccf1a3aad3328174ac86b691a5b2d
    MetroAE container started successfully
    
    >>> Pulling the latest templates and files for MetroAE config in the container
    
    Updating templates...
    
    MetroAE container setup complete. Execute 'metroae container status' for status.
    
    
    [MetroAE v3.3.0, script 1.0.4, container softlaunch]
    ```
    At this point the container should be running and the templates and VSD API spec should be installed in the specified data directory.
    ```
    [caso@metroae-host ~]$ docker ps
    CONTAINER ID        IMAGE                                                   COMMAND                  CREATED             STATUS              PORTS               NAMES
    574c7314aa7e        registry.mv.nuagenetworks.net:5000/metroae:softlaunch   "/bin/sh -c /sourc..."   2 minutes ago       Up 2 minutes                            metroae
    ```
    We can check the status via metroae. This will also show us the data directory mount point that was created during install.
    ```
    [caso@metroae-host ~]$ metroae container status
    
    >>> Checking docker version
    
    >>> Getting status of the MetroAE container
    
    >>> Getting the output of 'docker ps'
    
    CONTAINER
    574c7314aa7e
    
    >>> Getting the versions in the container itself
    
    Container version: "1.1.2"
    MetroÆ version: "v3.3.0"
    MetroÆ GUI version:  "0.1"
    
    >>> Getting container configuration from host
    
    MetroAE setup type: Config only
    MetroAE container data path: /home/caso/metroae_data
    
    [MetroAE v3.3.0, script 1.0.4, container softlaunch]
    ```
    The templates and the VSD API Specification should be downloaded and available in the path provided during setup.
    ```
    [caso@metroae-host ~]$ cd metroae_data/
    [caso@metroae-host metroae_data]$ ls -la
    total 36
    drwxrwxr-x.  7 caso   caso     167 Jul  9 18:25 .
    drwx------.  3 caso   caso      82 Jul  9 18:25 ..
    -rw-r--r--.  1 root   root       0 Jul  9 18:25 ansible.log
    drwxr-xr-x.  3 root   root      21 Jul  9 18:25 deployments
    drwxr-xr-x.  2 root   root    4096 Jul  9 18:25 Documentation
    drwxr-xr-x. 15 root   root    4096 Jul  9 18:25 examples
    -rw-r--r--.  1 root   root     399 Jul  9 18:25 id_rsa.pub
    -rw-r--r--.  1 root   root    5103 Jul  9 18:25 menu
    drwxr-xr-x.  5 root   root      72 Jul  9 18:25 standard-templates
    drwxrwxr-x.  2 centos centos 12288 Jul  9 18:25 vsd-api-specifications
    ```

7. Create and source an RC file.

    As detailed in the [Environment Variables guide](config-env-variables.md) we can use a RC file to fulfill the requirements of the command line. The format required is per below, replacing the values to fit the specific Setup

    ```
    [caso@metroae-host metroae_data]$ cat metroaerc
    export TEMPLATE_PATH=/metroae_data/standard-templates/templates
    export USER_DATA_PATH=/metroae_data/config/
    export VSD_SPECIFICATIONS_PATH=/metroae_data/vsd-api-specifications
    export VSD_URL=https://20.100.1.3:8443
    export VSD_USERNAME=csproot
    export VSD_PASSWORD=csproot
    export VSD_ENTERPRISE=csp
    ```

    Source the new file.

    ```
    [caso@metroae-host metroae_data]$ source metroaerc
    ```

    Can check the user environment

    ```
    [caso@metroae-host metroae_data]$ export | grep -E "VSD|_PATH"
    declare -x TEMPLATE_PATH="/metroae_data/standard-templates/templates"
    declare -x USER_DATA_PATH="/metroae_data/config/"
    declare -x VSD_ENTERPRISE="csp"
    declare -x VSD_PASSWORD="csproot"
    declare -x VSD_SPECIFICATIONS_PATH="/metroae_data/vsd-api-specifications"
    declare -x VSD_URL="https://20.100.1.3:8443"
    declare -x VSD_USERNAME="csproot"
    ```

metroae config is now ready to use. The operation of which is detailed in the Usage document <link to usage>
