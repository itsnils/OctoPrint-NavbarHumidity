# coding=utf-8
from __future__ import absolute_import

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import re

class NavBarPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin):

    def __init__(self):
        self.isRaspi = False

    def on_after_startup(self):
        if sys.platform == "linux2":
            with open('/proc/cpuinfo', 'r') as infile:
                    cpuinfo = infile.read()
            # Match a line like 'Hardware   : BCM2709'
            match = re.search('^Hardware\s+:\s+(\w+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

            if not match:
                # Couldn't find the hardware, assume it isn't a pi.
                self.isRaspi = False
            if match.group(1) == 'BCM2708':
                self._logger.debug("Pi 1")
                self.isRaspi = True
            elif match.group(1) == 'BCM2709':
                self._logger.debug("Pi 2")
                self.isRaspi = True

            if self.isRaspi:
                self._logger.debug("Let's start RepeatedTimer!")
                t = RepeatedTimer(1.0, self.checkRaspiTemp)
                t.start()
        # else:
        #     t = RepeatedTimer(5.0, self.checkRaspiTemp)
        #     t.start()

        self._logger.debug("is Raspberry Pi? - %s" % self.isRaspi)

    def checkRaspiTemp(self):
        import sarge

        self._logger.debug("Checking Raspberry Pi internal temperature")

        # if sys.platform == "linux2":
        p = sarge.run("/opt/vc/bin/vcgencmd measure_temp").returncode
        # else:
        #     import random
        #
        #     def randrange_float(start, stop, step):
        #         return random.randint(0, int((stop - start) / step)) * step + start
        #
        #     p = "temp=%s'C" % randrange_float(5, 60, 0.1)
        self._logger.debug("response: %s" % p)

        match = re.search('=(.*)\'', p)
        if not match:
            self.isRaspi = False
        else:
            temp = match.group(1)
            self._logger.debug("match: %s" % temp)
            self._plugin_manager.send_plugin_message(self._identifier, dict(israspi=self.isRaspi, raspitemp=temp))


    ##~~ AssetPlugin API
    
    def get_assets(self):
        return {
            "js": ["js/navbartemp.js"],
            "css": ["css/navbartemp.css"],
            "less": ["less/navbartemp.less"]
        } 
        
__plugin_name__ = "Navbar Temperature Plugin"
__plugin_implementation__ = NavBarPlugin()
