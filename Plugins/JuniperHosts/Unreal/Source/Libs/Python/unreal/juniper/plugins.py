import os

import juniper.paths
import juniper.utilities.json as json_utils
import juniper.utilities.filemgr
import unreal.juniper


def add_plugin(uplugin_path, symlink=True):
    """Adds a plugin to the current uproject"""
    if(os.path.isfile(uplugin_path)):

        client_settings_path = juniper.paths.find_config("client_settings.json")
        current_plugin_paths = json_utils.get_property(client_settings_path, "programs.unreal.plugin_paths")
        if(uplugin_path not in current_plugin_paths):
            plugin_paths = current_plugin_paths + [uplugin_path]
            json_utils.set_file_property(client_settings_path, "programs.unreal.plugin_paths", plugin_paths, local=True)

        plugin_dir = os.path.dirname(uplugin_path)
        plugin_dir_name = os.path.basename(plugin_dir)
        juniper.utilities.filemgr.create_junction(
            plugin_dir,
            os.path.join(unreal.juniper.unreal_project_dir(), "plugins", plugin_dir_name)
        )