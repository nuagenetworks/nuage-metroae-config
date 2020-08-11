# MetroAE Config

MetroAE Config is a template-driven VSD configuration tool. It utilizes the VSD API along with a set of common Feature Templates to create configuration in the VSD. You will create a yaml or json data file with the necessary configuration parameters for the particular feature and execute simple CLI commands to push the configuration into VSD. You can find out more about MetroAE Config by referring to [MetroAE Config Overview](CONFIG_OVERVIEW.md).

## How to install MetroAE Config

MetroAE Config is provided in a special verison of the MetroAE docker container. You can find out more about installation of MetroAE Config by referring to [How to Install MetroAE Config](CONFIG_INSTALLATION.md).  

## Where to get MetroAE Config

The installation and operation of MetroAE Config is handled by the `metroae` script. You can find the latest `metroae` script by opening [the MetroAE repo on github.com](https://raw.githubusercontent.com/nuagenetworks/nuage-metroae/master/metroae).  

## How to use MetroAE Config

MetroAE Config is a command-line-driven tool. Options are provided to validate, create, revert and update configuration in VSD, along with managing the feature teamplates. You can find out more about how to use MetroAE Config by referring to [MetroAE Config Usage](CONFIG_USAGE.md).

## Simplify the MetroAE Config command line with an RC file

Executing MetroAE Configuration requires details such as location of the VSD API Specification, feature templates, config data and the VSD we are configuring. We can simplify this by creating an RC file. You can find out more about how to use environment variables with MetroAE Config by referring to [MetroAE Config Environment Variables](CONFIG_ENV_VARIABLES.md).  

## Features Supported by MetroAE Config

MetroAE Config will provide support for a growing list of VSD features. You can find a list of the current features supported by referring to [MetroAE Feature Documentation](../standard-templates/documentation/README.md).

## Feature Samples

Each support feature has an example of user input provided for your reference. You can find out more about the supported features by referring to [MetroAE Config User Data Samples](../standard-templates/examples).

## Inheritance

When creating configuration user data to pass into MetroAE Config you can make use of `inheritance` to avoid specifying common parameters multiple times. You can find out more about inheritance by refrring to [MetroAE Inheritance](CONFIG-INHERITANCE.md).

## Questions, Feedback, and Contributing

Get support via the [forums](https://devops.nuagenetworks.net/forum/) on the [MetroAE site](https://devops.nuagenetworks.net/).

Ask questions and contact us directly at [devops@nuagenetworks.net](mailto:devops@nuagenetworks.net "send email to nuage-metro project").

Report bugs you find and suggest new features and enhancements via the [GitHub Issues](https://github.com/nuagenetworks/nuage-metroae/issues "nuage-metroae issues") feature.

You may also [contribute](CONTRIBUTING.md) to MetroAE by submitting your own code to the project.
