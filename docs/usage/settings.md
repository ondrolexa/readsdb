# Settings

The settings used by the plugin are integrated into QGIS `Settings` > ![QGIS mActionOptions](https://docs.qgis.org/3.44/en/_images/mActionOptions.png) `Options...` menu:

![QGIS - General settings panel](https://docs.qgis.org/3.44/en/_images/options_general.png)

----

## Environment variables

Most of parameters can be defined via environment variables. This allows plugin configuration to be managed directly by the IT Department or tools like [QGIS Deployment Toolbelt (QDT)](https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/jobs/environment_variables.html). It offers different scopes:

- for every QGIS profiles on a computer (requires admin access level)
- for every QGIS profiles in an user session
- in a specific QGIS profile: see `Preferences` > `System` and `Environment variables` panel (see the [relevant section in the official documentation](https://docs.qgis.org/3.44/en/docs/user_manual/introduction/qgis_configuration.html#system-settings))
- during a QGIS session only once: set it in the command line when launching QGIS, for example: `QGIS_READSDB_DEBUG_MODE=true qgis` or `env QGIS_READSDB_DEBUG_MODE=true qgis` depending on your system.

For example, in a classic Linux system, if you want to enable GitLab notifications and include QGIS and plugins in new issues for every QGIS profile in your user session, you can add the following lines to your `.bashrc`, `.zshrc`, or `.profile` file:

```sh
export QGIS_READSDB_DEBUG_MODE="true"
```

On Windows, it's even more simple, there is a GUI to set environment variables to both system (admin) and user scopes. Find it through your start menu.

The following table lists the available parameters with their associated environment variable and default value:

| Parameter         | Environment variable                         | Default value                |
| :---------------- | :------------------------------------------: | :--------------------------: |
| Enable debug mode | `QGIS_READSDB_DEBUG_MODE` | `False` |
