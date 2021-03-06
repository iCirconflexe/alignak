# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.
"""This module provide a specific HTTP interface for a Broker."""
import cherrypy
from alignak.http.generic_interface import GenericInterface
from alignak.misc.serialization import unserialize


class BrokerInterface(GenericInterface):
    """This class provides specific HTTP functions for Broker."""

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def push_broks(self):
        """Push broks objects to the daemon (internal)
        Only used on a Broker daemon by the Arbiter

        :return: None
        """
        broks = cherrypy.request.json
        with self.app.arbiter_broks_lock:
            self.app.arbiter_broks.extend([unserialize(elem, True) for
                                           elem in broks['broks'].values()])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_raw_stats(self):
        """
        Get stats (queue size) for each modules

        :return: list of modules with queue_size
        :rtype: list
        """
        app = self.app
        res = {
            'modules_count': len(app.modules_manager.instances)
        }

        insts = [inst for inst in app.modules_manager.instances if inst.is_external]
        for inst in insts:
            try:
                res[inst.uuid] = {'module_alias': inst.get_name(),
                                  'module_types': inst.get_types(),
                                  'queue_size': inst.to_q.qsize()}
            except Exception:  # pylint: disable=W0703
                res[inst.uuid] = {'module_alias': inst.get_name(),
                                  'module_types': inst.get_types(),
                                  'queue_size': 0}

        return res
