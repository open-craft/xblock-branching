# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 edX
#
# Authors:
#          Alan Boudreault <alan@alanb.ca>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# Imports ###########################################################

import logging

from xblock.core import XBlock
from xblock.fields import String, Scope
from web_fragments.fragment import Fragment

from problem_builder.mcq import MCQBlock
from problem_builder.mixins import EnumerableChildMixin, StepParentMixin
from adventure.utils import loader
from video_xblock import VideoXBlock

# Globals ###########################################################

log = logging.getLogger(__name__)

# Classes ###########################################################


class StepBlock(EnumerableChildMixin, StepParentMixin, XBlock):
    """
    A representation of an adventure step.

    Note that it is also a StepParentMixin, as MCQs are of StepMixin,
    requiring there parents to be so.
    """
    content = String(help="Text of the info to provide if needed", scope=Scope.content, default="")
    name = String(help="Name of the step", scope=Scope.content, default=None)
    back = String(help="Name of the back step", scope=Scope.content, default=None)
    next = String(help="Name of the next step", scope=Scope.content, default=None)
    has_children = True

    def render(self, context=None):
        """
        Returns a fragment containing the formatted step
        """
        context = context or {}
        fragment = Fragment()
        child_contents = []

        for child_id in self.children:
            child = self.runtime.get_block(child_id)
            if child is None:
                child_contents.append("<p>[Error: Unable to load child component.]</p>")
            else:
                child_fragment = child.student_view(context)
                fragment.add_fragment_resources(child_fragment)
                child_contents.append(child_fragment.content)
        
        html = loader.render_template('templates/html/step.html', {
            'self': self,
            'children': child_contents
        })
        fragment.add_content(html)
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/adventure_step_view.js'))
        fragment.initialize_js('StepBlock')
        return fragment

    @property
    def has_choices(self):
        """
        Returns True if the current_step has choices.
        """

        choices = [child for child in self.get_children_objects() if isinstance(child, MCQBlock)]

        return bool(choices)

    @property
    def video_blocks(self):
        """
        Returns a list of child blocks that are instances of VideoBlock.
        """
        return [child for child in self.get_children_objects() if isinstance(child, VideoXBlock)]
