"""
Base implementation for Juniper support in Houdini
"""
import os
import shlex
import winreg

import juniper.engine


class Houdini(juniper.engine.JuniperEngine):
    def on_pre_startup(self):
        """
        Adds the `hou.juniper` package to the `hou.__path__`
        """
        import hou
        hou.__path__.append(os.path.join(
            self.workspace_root,
            "Source\\Hosts\\Houdini\\Source\\Libs\\Python\\hou"
        ))

    def on_install(self):
        """
        Installs the Juniper bootstrap to Houdini.
        TODO? This overrides the pythonrc.py file - which is destructive. Swap out?
        """
        try:
            hip_exe_path = self.__get_default_windows_app('.hip').lower()
            h_python_scripts_dir = os.path.join(
                hip_exe_path.split("bin")[0],
                "houdini\\scripts\\python"
            )
            bootstrap_file_path = os.path.join(h_python_scripts_dir, "pythonrc.py")

            self.create_bootstrap_file(bootstrap_file_path)
        except Exception:
            juniper.log.error("Failed to initialize Houdini juniper environment.", silent=True)

    # ----------------------------------------------------------------------

    def __get_default_windows_app(self, suffix):
        class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
            command = winreg.QueryValueEx(key, '')[0]
            return shlex.split(command)[0]
