## MetroAE Config - Overview

*metroae config* is command line driven tool that allows configuration to be created and deleted within the VSD using configuration templates.


##### What is MetroAE Config  

MetroAE Config is a template driven VSD configuration tool. It utilizes the VSD API along with a set of common Feature Templates to create configuration in the VSD. The user will create a yaml or json data file with the necessary configuration parameters for the particular feature and execute a simple CLI command *"metroae config create"* to push the configuration into VSD. See [MetroAE Config usage](config-usage.md).    


##### How is MetroAE Config delivered

MetroAE Config is part of the wider MetroAE platform. However it is only supported in the container based version of MetroAE. All necessary components are provided within the container and in part during the metroae config setup process. See [Installation and Setup](config-installation.md).  


##### What is a Feature Template

A feature template is a provided yaml file that defines the data required by the VSD along with API interaction to create specific configuration in the VSD. MetroAE config provides a set of supported Feature Templates that cover specific feature configuration in the VSD. Feature Templates do not need to have a 1 to 1 relationship with a VSD object, these can be abstracted to simplify the user data requirements. See [Description of a Feature Template](config-feature-template-overview.md).  


##### Who provides the Feature Templates

MetroAE Config provides a supported set of Feature Templates and will continue to grow the list to cover more portions of VSD configuration along with greater work flow, user data and feature abstraction. The Feature Templates are authored and tested by the Nuage CASO team. It is the intention to also provide experimental and community authored templates as we grow the user community for the tool.  


##### How is it different than VSPK?

The Nuage VSPK is a set of libraries provided in multiple frameworks that allow a user to interact with the VSD API. The frameworks supported are common tools sets like python, ansible and Go. To utilize the VSPK the user will have to understand the necessary API objects, calls and relationships and subsequently script (in the chosen language) the configuration work flow that is required. VSPK is a powerful tool and is often used to integrate the Nuage VSD into north bound OSS and configuration portals etc.  

However for users who are not well versed in one of the frameworks supported and may not be proficient at programming/scripting there is still a gap. Of course, the VSD provides a rich UI. However, for repeated configurations and complex network designs, the UI is not very efficient and can be prone to human error, particularly when dealing with large configurations or advanced features.  

MetroAE Config takes a different approach to the configuration challenge. Rather than exposing a library and having the user develop code, a template driven approach to configuration is provided. Templates are authored to interact directly with the VSD API, abstracting the API calls, objects and relationships away from the user. The user needs to provide the required "data" for a particular feature and the MetroAE Config engine handles all the API interaction.
