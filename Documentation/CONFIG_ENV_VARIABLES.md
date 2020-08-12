# MetroAE Config - Simplified Operations by Exporting Environment Variables With an RC File

In order to execute actions against the VSD, you must provide local path information and authentication credentials to the configuration engine.

Instead of specifying each requirement at the command line individually, you can pass the information to the engine with environment variables by:

1. Creating an RC file on the local client which sets the required variables in your current shell, and
2. sourcing that file.

## Create RC File

Create a file containing the following parameters. See parameter details below.

```
export TEMPLATE_PATH=/metroae_data/standard-templates/templates
export USER_DATA_PATH=/metroae_data/configuration/
export VSD_SPECIFICATIONS_PATH=/metroae_data/vsd-api-specifications
export VSD_URL=https://10.101.0.28:8443
export VSD_USERNAME=csproot
export VSD_PASSWORD=csproot
export VSD_ENTERPRISE=csp
```

### Parameter Details

The first three parameters specify paths on the local client where the configuration engine is running.  

**TEMPLATE_PATH** - path to feature templates. Default is shown below. Do not change the path unless you are using non-standard/modified templates.  

```
TEMPLATE_PATH=/metroae_data/standard-templates/templates
```

**USER_DATA_PATH** - location/directory of user data templates that will be used to configure VSD. Sample templates are provided in the default installation. However, in most cases the directory is user-defined.  

```
USER_DATA_PATH=/metroae_data/configuration/
```

**VSD_SPECIFICATIONS_PATH** - location/path of the VSD API Specifications. The specifications are downloaded and installed in the default location shown below as part of template install/update.

```
VSD_SPECIFICATIONS_PATH=/metroae_data/vsd-api-specifications
```

The next four parameters specify details about configuring the target VSD.

**VSD_URL** - URL of the target VSD to be configured

```
VSD_URL=https://10.101.0.28:8443
```

**VSD_USERNAME** - username of the account that will be configuring the VSD. This username is used by the administrator to access the VSD UI. Default is shown below.

```
VSD_USERNAME=csproot
```

**VSD_PASSWORD** - password of the account that will be configuring the VSD. This is the password that is used by the administrator to access the VSD UI. Default is shown below.

```
VSD_PASSWORD=csproot
```

**VSD_ENTERPRISE** - enterprise that the user account is configured to access in the VSD. Default is shown below.

```
VSD_ENTERPRISE=csp
```

## Source RC File

You give the configuration engine access to the environment parameters for your user environment by sourcing the file you created with the command below, substituting `<rcfilename>` with the name of your RC file.

```
[root@metroae]# source <rcfilename>
```
## Overriding Environment Variables

If, for any environment variable, you want to specify a different value than the one specified in the RC file, you don't need to copy the file and source it again. You can override any environment value at the command line by adding the option *--datapath* to the command.

For example, if your RC file specifies the user data path as:  

```
USER_DATA_PATH=/metroae_data/configuration/
```
And you want to create an enterprise with the user data path as /metroae_data/demo/ instead, then run the command below to override the RC file value.

```
[root@metroae]# metroae config create enterprise-default.yaml --datapath /metroae_data/demo/
```

Overriding is supported for all command line variables. You can find out more about command line usage by referring to [MetroAE Command Line Usage](CONFIG_USAGE.md).
