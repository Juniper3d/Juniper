import os
import shutil
import shlex
import winreg

import juniper
import juniper.framework.backend.plugin
import juniper.paths


def get_default_windows_app(suffix):
    class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
        command = winreg.QueryValueEx(key, '')[0]
        return shlex.split(command)[0]


try:
    hip_exe_path = get_default_windows_app('.hip').lower()
    h_python_scripts_dir = os.path.join(
        hip_exe_path.split("bin")[0]
        + "houdini\\scripts\\python"
    )

    if(os.path.isdir(juniper.paths.root())):
        plugin = juniper.framework.backend.plugin.PluginManager().find_plugin("houdini")
        startup_script = os.path.join(plugin.root, "Source\\Bootstrap\\__bootstrap__.py")
        if(not os.path.isdir(h_python_scripts_dir)):
            os.mkdir(h_python_scripts_dir)
        shutil.copyfile(startup_script, os.path.join(h_python_scripts_dir, "pythonrc.py"))
except Exception:
    juniper.log.error("Failed to initialize Houdini juniper environment.", silent=True)