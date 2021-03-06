"""
TODO! Replace this with the version in bootstrap and merge contents
"""
import juniper.paths
import juniper.engine.types.script
import juniper.types.framework.singleton
import juniper.utilities.string as string_utils

import functools
import glob
import json
import os
import sys


class PluginManager(object, metaclass=juniper.types.framework.singleton.Singleton):
    def __init__(self):
        self.plugin_cache = []

        # Initialize all avaliable plugins
        # TODO~ Add in a system to enable/disable plugins (with a GUI for user setting)
        plugins_root = os.path.join(juniper.paths.root(), "Plugins")
        for plugin_group in os.listdir(plugins_root):
            plugin_group_dir = os.path.join(plugins_root, plugin_group)
            if(os.path.isdir(plugin_group_dir)):
                for plugin_name in os.listdir(plugin_group_dir):
                    plugin_dir = os.path.join(plugin_group_dir, plugin_name)
                    if(os.path.isdir(plugin_dir)):
                        for i in os.listdir(plugin_dir):
                            if(i.endswith(".jplugin")):
                                jplugin_path = os.path.join(plugin_dir, i)
                                self.plugin_cache.append(Plugin(jplugin_path))

        # Sort all avaliable plugins to ensure order of execution is adhered to:
        # 1) Juniper host plugins should always be first - as these have the most control over the workspace
        # 2) Juniper plugins should always come after host plugins so any worksplace additions are initialized
        # 3) All other plugins should come last
        juniper_plugins = []
        juniper_host_plugins = []
        other_plugins = []

        for i in self.plugin_cache:
            if("\\juniperhosts\\" in i.root.lower()):
                juniper_host_plugins.append(i)
            elif("\\juniper\\" in i.root.lower()):
                juniper_plugins.append(i)
            else:
                other_plugins.append(i)

        self.plugin_cache = juniper_host_plugins + juniper_plugins + other_plugins

        # Add all plugin python roots to the `__path__` for this module so they can be accessed via `juniper.plugins.plugin_name`
        '''for i in self.plugin_cache:
            sys.modules[__name__].__path__.append(
                os.path.join(i.root, "Source\\Libs\\Python")
            )'''

    @property
    def current_host_plugin(self):
        """
        :return <Plugin:host> The current host plugin (Ie, max, designer, etc)
        """
        for i in self.plugin_cache:
            if("\\juniperhosts\\" in i.root.lower() and i.enabled):
                return i
        return None

    def __iter__(self):
        """
        Override the iterator method for the PluginManager to iterate over all available plugins
        :yield <Plugin:plugin> The current plugin
        """
        for i in self.plugin_cache:
            yield i

    def find_plugin(self, plugin_name):
        """
        Finds a plugin by its name
        :param <str:plugin_name> The name of the plugin to find
        :return <Plugin:plugin> The plugin if found - else None
        """
        plugin_name = plugin_name.lower()
        for i in self.plugin_cache:
            if(i.name == plugin_name):
                return i
        return None


class Plugin(object):
    def __init__(self, jplugin_path):
        self.jplugin_path = jplugin_path

    def __repr__(self):
        return f"Plugin(\"{self.jplugin_path}\")"

    @property
    @functools.lru_cache()
    def plugin_metadata(self):
        """
        :return <dict:metadata> The jplugin loaded as a dict
        """
        with open(self.jplugin_path, "r") as f:
            return json.load(f)

    @property
    @functools.lru_cache()
    def root(self):
        """
        :return <str:root> The root directory of this plugin
        """
        return os.path.dirname(self.jplugin_path)

    @property
    @functools.lru_cache()
    def name(self):
        """
        :return <str:name> The name of this plugin
        """
        return os.path.basename(self.jplugin_path).split(".")[0]

    @property
    @functools.lru_cache()
    def display_name(self):
        """
        :return <str:name> The friendly name of this plugin
        """
        return string_utils.snake_to_name(self.name)

    @property
    @functools.lru_cache()
    def enabled(self):
        """
        :return <bool:enabled> True if this plugin is enabled - else False
        """
        # If this is a host plugin (Ie, max, designer), and we're not in the context
        # the plugin should be disabled
        if("\\juniperhosts\\" in self.root.lower()):
            if(self.name != juniper.program_context):
                return False
        if("enabled" in self.plugin_metadata):
            return self.plugin_metadata["enabled"]
        return True

    @property
    @functools.lru_cache()
    def internal(self):
        """
        :return <bool:internal> True if this is an internal (Juniper) plugin - else False
        """
        with open(self.jplugin_path, "r") as f:
            json_data = json.load(f)
            if("internal" in json_data):
                return json_data["internal"] is True
        return False

    # ---------------------------------------------------------------------

    def get_file(self, subdir, relative_path, override=None, require_override=False):
        """
        Gets a file for the plugin - with optional overrides
        :param <str:subdir> The name of the base directory to search
        :param <str:relative_path> The relative path for the file
        :param [<str:override>] Optional override for the file (Ie, "some_file.designer.txt")
        :param [<bool:require_override>] Is the override required? Or may we fallback to the non-overriden version
        :return <str:output> The file if found - else None
        """
        file_root = os.path.join(self.root, subdir)

        if(override):
            filename, _, filetype = relative_path.rpartition(".")
            override_relative_path = f"{filename}.{override}.{filetype}"
            override_abs_path = os.path.join(file_root, override_relative_path)
            if(os.path.isfile(override_abs_path)):
                return override_abs_path
            elif(require_override):
                return None

        abs_path = os.path.join(file_root, relative_path)
        if(os.path.isfile(abs_path)):
            return abs_path
        return None

    def get_resource(self, relative_path, override=None, require_override=False):
        """
        Gets a resource for the plugin - with optional overrides
        :param <str:relative_path> The relative path for the file
        :param [<str:override>] Optional override for the file (Ie, "some_file.designer.txt")
        :param [<bool:require_override>] Is the override required? Or may we fallback to the non-overriden version
        :return <str:output> The file if found - else None
        """
        return self.get_file("Resources", relative_path, override=override, require_override=require_override)

    def get_config(self, relative_path, override=None, require_override=False):
        """
        Gets a config for the plugin - with optional overrides
        :param <str:relative_path> The relative path for the file
        :param [<str:override>] Optional override for the file (Ie, "some_file.designer.txt")
        :param [<bool:require_override>] Is the override required? Or may we fallback to the non-overriden version
        :return <str:output> The file if found - else None
        """
        return self.get_file("Config", relative_path, override=override, require_override=require_override)

    # ---------------------------------------------------------------------


# TODO~ Plugin Creator
'''
class ModuleCreator(object):
    def __init__(self, module_name, module_display_name, integration_type="standalone"):
        """
        Helper class used to create a Juniper Module
        :param <str:module_name> The code name of the module (Ie, "tools_library")
        :param <str:module_display_name> The display name of the module (Ie, "Tools Library")
        :param [<str:integration_type>] How are tools from this module integrated into Juniper?
        """
        self.module_name = module_name
        self.module_display_name = module_display_name
        self.integration_type = integration_type

    @property
    def integration_types(self):
        """
        :return <[str]:integration_types> All vaild integration types
        """
        return (
            "Integrated",
            "Standalone",
            "Separate"
        )

    @property
    def jmodule_root(self):
        """
        :return <str:root> The root directory of this module
        """
        return os.path.join(juniper.paths.root(), "modules", self.module_display_name)

    @property
    def jmodule_path(self):
        """
        :return <str:path> The path to the module.jmodule file
        """
        return os.path.join(self.jmodule_root, self.module_name + ".jmodule")

    @property
    def jmodule_data(self):
        """
        :return <dict:data> The data that should be contained in the .jmodule file
        """
        return {
            "integration_type": self.integration_type
        }

    def create(self):
        """
        Creates all stub files for this juniper module
        """
        if(self.module_name):
            output_root = self.jmodule_root
            jmodule_path = self.jmodule_path

            paths = [
                f"{output_root}\\bin\\common\\.empty",
                f"{output_root}\\config\\common\\.empty",
                f"{output_root}\\lib\\python\\{self.module_name}\\__init__.py",
                f"{output_root}\\resources\\common\\.empty",
                f"{output_root}\\scripts\\common\\.empty",
                f"{output_root}\\shelves\\.empty"
            ]

            for i in paths:
                if(not os.path.isfile(i)):
                    os.makedirs(os.path.dirname(i))
                    with open(i, "w") as f:
                        f.write("")

            if(not os.path.isfile(jmodule_path)):
                with open(jmodule_path, "w") as f:
                    json.dump(self.jmodule_data, f, sort_keys=True)
'''
