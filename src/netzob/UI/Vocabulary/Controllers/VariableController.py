# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.DataTypes.AbstractType import AbstractType
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.DataTypes.DecimalWordType import \
    DecimalWordType
from netzob.Common.MMSTD.Dictionary.DataTypes.HexWordType import HexWordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IPv4WordType import IPv4WordType
from netzob.Common.MMSTD.Dictionary.DataTypes.IntegerType import IntegerType
from netzob.Common.MMSTD.Dictionary.DataTypes.MACWordType import MACWordType
from netzob.Common.MMSTD.Dictionary.DataTypes.WordType import WordType
from netzob.Common.MMSTD.Dictionary.RelationTypes.AbstractRelationType import \
    AbstractRelationType
from netzob.Common.MMSTD.Dictionary.RelationTypes.WordSizeRelationType import \
    WordSizeRelationType
from netzob.Common.MMSTD.Dictionary.RelationTypes.BinarySizeRelationType import \
    BinarySizeRelationType
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.ComputedRelationVariable import \
    ComputedRelationVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import \
    RepeatVariable
from netzob.UI.Vocabulary.Views.VariableView import VariableTreeView, \
    VariableCreationView, VariableMovingView
from netzob.UI.NetzobWidgets import NetzobErrorMessage


class VariableTreeController(object):
    """VariableTreeController:
            Controls a variable's tree view display
    """

    # Indexes of variable in the variable type combo box.
    VARIABLE_INDEX_LIST = []

    # Indexes of DataVariable type in the type combo box.
    TYPE_INDEX_LIST = []

    # Index of ComputedRelationVariable type in the relation type combo box.
    RELATION_TYPE_INDEX_LIST = []

    def __init__(self, netzob, symbol, field):
        """Constructor of VariableTreeController:

                @type netzob: netzob.Common.NetzobGui.NetzobGui
                @param netzob: the main netzob project.
                @type field: netzob.Common.Field.Field
                @param field: the field, the variable of which we want to display.
        """
        self.netzob = netzob
        self.symbol = symbol
        self.field = field

        self.view = VariableTreeView(self)
        self.view.getWidg("dialog").set_title(_("Configure definition domain for the field: {0}").format(field.getName()))
#        if self.field.getVariable() is not None:
        self.registerContent(self.field.getVariable())
        self.initIndexesList()
        self.initCallbacks()

    def initIndexesList(self):
        """initIndexesList:
                Initiate the indexes list. These list keep links between index in combo box and type.
        """
        VariableTreeController.VARIABLE_INDEX_LIST = [AggregateVariable.TYPE, AlternateVariable.TYPE, ComputedRelationVariable.TYPE, DataVariable.TYPE, RepeatVariable.TYPE]
        VariableTreeController.TYPE_INDEX_LIST = [BinaryType.TYPE, DecimalWordType.TYPE, HexWordType.TYPE, IntegerType.TYPE, IPv4WordType.TYPE, MACWordType.TYPE, WordType.TYPE]
        VariableTreeController.RELATION_TYPE_INDEX_LIST = [BinarySizeRelationType.TYPE, WordSizeRelationType.TYPE]

    def initCallbacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("treeview").connect('button-press-event', self.showMenu)
        self.view.getWidg("button").connect('clicked', self.view.destroyDialog)
        self.view.getWidg("createDefaultVariable_button").connect('clicked', self.createDefaultVariable_cb)

    def registerContent(self, variable):
        """registerContent:
                Register each variable, their entry in the tree view.
                Fill the tree view of a variable with all its displayable content.

                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the root variable which content will be displayed.
        """
        self.dictVariable = dict()
        self.dictEntry = dict()

        self.treestore = Gtk.TreeStore(str, str)  # id of the data, description
        self.registerVariable(None, variable)
        self.view.getWidg("treeview").set_model(self.treestore)

    def registerVariable(self, rootEntry, variable):
        """registerVariable:
                Register a variable in the tree view under its root variable (Aggregate or Alternate).
                May be recursive.

                @type rootEntry: Gtk.treerow
                @param rootEntry: the root entry under which we will add this entry.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the variable which will be added to the tree view representation.
        """
        if variable is None:
            return
        self.dictVariable[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), variable.toString()])
        self.dictEntry[str(variable.getID())] = newEntry
        if variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE:
            if variable.getChildren() is not None:
                for child in variable.getChildren():
                    self.registerVariable(newEntry, child)
        if variable.getVariableType() == RepeatVariable.TYPE:
            if variable.getChild() is not None:
                self.registerVariable(newEntry, variable.getChild())

    def showMenu(self, treeview, event):
        """showMenu:
                Called on right click on a variable.

                @param treeview: the treeview which contains the triggering variable.
                @param event: the mouse event which called this function.
        """
        variable = None
        if event.button == 3:
            try:
                x = int(event.x)
                y = int(event.y)
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

                # Retrieve the selected variable
                varid = None
                aniter = treeview.get_model().get_iter(path)
                if aniter:
                    if treeview.get_model().iter_is_valid(aniter):
                        varid = treeview.get_model().get_value(aniter, 0)

                        if varid is not None:
                            variable = self.dictVariable[varid]
            except:
                logging.debug(_("The user clicks on no variable."))
        else:
            # Wrong mouse click
            return

        if variable is None:
            logging.debug("Impossible to find the selected variable.")
            return

        # We display the menu for the insertion of sub-elements if its an Aggregate or an Alternative
        self.menu = Gtk.Menu()

        # We can add elements only to node variable.
        if variable.isNode():
            if variable.getVariableType() == RepeatVariable.TYPE:
                # Add an element to a repeat variable will replace the previous one.
                itemAdd = Gtk.MenuItem(_("Edit the sub-element"))
            else:
                itemAdd = Gtk.MenuItem(_("Add a sub-element"))
            itemAdd.connect("activate", VariableCreationController, self, variable, aniter, False)
            itemAdd.show()
            self.menu.append(itemAdd)

        # To edit an element.
        itemEdit = Gtk.MenuItem(_("Edit this element"))
        itemEdit.connect("activate", VariableCreationController, self, variable, aniter, True)
        itemEdit.show()

        # If we have not click on the root variable, we can move and remove it. The root variable can be edited. it is way enough.
        if variable.getID() != self.field.getVariable().getID():
            # To move an element.
            itemMove = Gtk.MenuItem(_("Move this element"))
            itemMove.connect("activate", VariableMovingController, self, variable)
            itemMove.show()
            self.menu.append(itemMove)

            # To remove an element.
            itemRemove = Gtk.MenuItem(_("Remove this element"))
            itemRemove.connect("activate", self.removeVariable, variable)
            itemRemove.show()
            self.menu.append(itemRemove)

        self.menu.append(itemEdit)
        self.menu.popup(None, None, None, None, event.button, event.time)

    def removeVariable(self, item, variable):
        """removeVariable:
                Remove a variable and its presence in the tree view.

                @type item: Gtk.Menuitem
                @param item: the menu item which calls this function.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be removed.
        """
        questionMsg = _("Click yes to confirm the removal of the variable {0}").format(variable.getName())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            # Remove the variable from the global tree.
            father = variable.getFathers()[0]
            father.removeChildByID(variable)
            # Remove its entry.
            entry = self.dictEntry[str(variable.getID())]
            self.treestore.remove(entry)

            # Remove the variable and its entry from dictionaries.
            self.dictEntry.pop(str(variable.getID()))
            self.dictVariable.pop(str(variable.getID()))

        else:
            logging.info("The user didn't confirm the deletion of the variable {0}".format(variable.getName()))

    def editVariable(self, variable):
        """editVariable:
                Edit a variable and its representation on the tree row.

                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be edited.
        """
        questionMsg = _("Click yes to confirm the edition of the variable {0}").format(variable.getName())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()

        if result == Gtk.ResponseType.YES:
            pass
            # The root variable.
            if variable.getID() == self.field.getVariable().getID():
                # Edit the variable
                self.field.setVariable(variable)

                # Update its entry
                entry = self.dictEntry[variable.getID()]
                self.treestore.remove(entry)
                self.registerVariable(None, variable)
            # Other variables.
            else:
                # Edit the variable
                father = variable.getFathers()[0]
                father.editChildByID(variable)

                logging.debug("variable: {0}, fathers: {1}".format(variable.getName(), variable.getFathers()))

                # Update its entry
                entry = self.dictEntry[variable.getID()]
                self.treestore.set_value(entry, 1, variable.toString())
                self.dictVariable[variable.getID()] = variable
        else:
            logging.info("The user didn't confirm the edition of the variable {0}".format(variable.getName()))

    def createDefaultVariable_cb(self, event):
        """createDefaultVariable_cb:
                Create a default variable, which is an alternate of
                all the possible values of the field.
        """
        self.field.generateDefaultVariable(self.symbol)
        self.registerContent(self.field.getVariable())


class VariableCreationController(object):
    """VariableCreationController:
            Manage a view that allows the user to modify/create a variable by specifying each of its field.
    """

    def __init__(self, item, treeController, variable, rootEntry, editOverCreate):
        """Constructor of VariableCreationController:
                Called by a click on the tree view of all variables.

                @type item: Gtk.Menuitem
                @param item: the menu item that calls this constructor.
                @type treeController: VariableTreeController
                @param treeController: the controller of the tree view which cause this controller's view to appear.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be modified/to which we will add a child.
                @type rootEntry: Gtk.treerow
                @param rootEntry: the root entry associates to the variable in the treestore.
                @type editOverCreate: boolean
                @param editOverCreate: True if we want to edit the selected variable, false if we want to create a new variable.
        """
        self.treeController = treeController
        self.netzob = self.treeController.netzob
        self.variable = variable
        self.rootEntry = rootEntry
        self.editOverCreate = editOverCreate
        self.view = VariableCreationView(self)
        self.initCallBacks()
        self.runDialog()

    def initCallBacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("variableTypeCombo").connect('changed', self.updateOptions)
        self.view.getWidg("minSpin").connect('changed', self.updateMaxSpin)
        self.view.getWidg("applyButton").connect("clicked", self.validateChanges)
        self.view.getWidg("IDButton").connect("clicked", self.chooseSelectedVariable)
        self.view.getWidg("sizedCheck").connect('toggled', self.updateDelimiterAndSize)

    def updateOptions(self, widget=None):
        """updateOptions:
                Update the shown options of the variable creation view to set visible only those which are useful.

                @type widget: Gtk.widget
                @param widget: the widget which modification calls this function.
        """
        varTypeIndex = self.view.getWidg("variableTypeCombo").get_active()
        handler_id = None

        # Aggregate or alternate variable
        if varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(AggregateVariable.TYPE) or varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(AlternateVariable.TYPE):
            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("relationTypeLabel").set_visible(False)
            self.view.getWidg("sizedLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)

            self.view.getWidg("relationTypeCombo").set_visible(False)
            self.view.getWidg("IDGrid").set_visible(False)
            self.view.getWidg("IDLabel").set_visible(False)
            self.view.getWidg("IDEntry").set_visible(False)
            self.view.getWidg("IDButton").set_visible(False)
            self.view.getWidg("sizedCheck").set_visible(False)

            self.view.getWidg("factorLabel").set_visible(False)
            self.view.getWidg("factorEntry").set_visible(False)
            self.view.getWidg("offsetLabel").set_visible(False)
            self.view.getWidg("offsetEntry").set_visible(False)

            self.updateDelimiterAndSize(default=True)

            if handler_id is not None:
                object.disconnect(handler_id)
                handler_id = None

        # Computed Relation variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(ComputedRelationVariable.TYPE):
            self.view.getWidg("minLabel").set_text("Minimum number of characters")
            self.view.getWidg("maxLabel").set_text("Maximum number of characters")

            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("relationTypeLabel").set_visible(True)
            self.view.getWidg("sizedLabel").set_visible(True)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)

            self.view.getWidg("relationTypeCombo").set_visible(True)
            self.view.getWidg("IDGrid").set_visible(True)
            self.view.getWidg("IDLabel").set_visible(True)
            self.view.getWidg("IDEntry").set_visible(True)
            self.view.getWidg("IDButton").set_visible(True)
            self.view.getWidg("sizedCheck").set_visible(True)

            self.view.getWidg("factorLabel").set_visible(True)
            self.view.getWidg("factorEntry").set_visible(True)
            self.view.getWidg("offsetLabel").set_visible(True)
            self.view.getWidg("offsetEntry").set_visible(True)

            self.updateDelimiterAndSize()

            if handler_id is not None:
                object.disconnect(handler_id)
                handler_id = None

        # Data variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(DataVariable.TYPE):
            self.view.getWidg("valueLabel").set_text("Original Value")
            self.view.getWidg("minLabel").set_text("Minimum number of characters")
            self.view.getWidg("maxLabel").set_text("Maximum number of characters")

            self.view.getWidg("valueLabel").set_visible(True)
            self.view.getWidg("typeLabel").set_visible(True)
            self.view.getWidg("relationTypeLabel").set_visible(False)
            self.view.getWidg("sizedLabel").set_visible(True)

            self.view.getWidg("valueEntry").set_visible(True)
            self.view.getWidg("typeCombo").set_visible(True)

            self.view.getWidg("relationTypeCombo").set_visible(False)
            self.view.getWidg("IDGrid").set_visible(False)
            self.view.getWidg("IDLabel").set_visible(False)
            self.view.getWidg("IDEntry").set_visible(False)
            self.view.getWidg("IDButton").set_visible(False)
            self.view.getWidg("sizedCheck").set_visible(True)

            self.view.getWidg("factorLabel").set_visible(False)
            self.view.getWidg("factorEntry").set_visible(False)
            self.view.getWidg("offsetLabel").set_visible(False)
            self.view.getWidg("offsetEntry").set_visible(False)

            self.updateDelimiterAndSize()

            handler_id = self.view.getWidg("valueEntry").connect('changed', self.updateMinSpin)

        # Repeat variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(RepeatVariable.TYPE):
            self.view.getWidg("minLabel").set_text("Minimum number of iterations")
            self.view.getWidg("maxLabel").set_text("Maximum number of iterations")

            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("relationTypeLabel").set_visible(False)
            self.view.getWidg("sizedLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)

            self.view.getWidg("relationTypeCombo").set_visible(False)
            self.view.getWidg("IDGrid").set_visible(False)
            self.view.getWidg("IDLabel").set_visible(False)
            self.view.getWidg("IDEntry").set_visible(False)
            self.view.getWidg("IDButton").set_visible(False)
            self.view.getWidg("sizedCheck").set_visible(False)

            # Min/Max/Delimiter.
            self.view.getWidg("minLabel").set_visible(True)
            self.view.getWidg("maxLabel").set_visible(True)
            self.view.getWidg("delimiterLabel").set_visible(False)

            self.view.getWidg("minSpin").set_visible(True)
            self.view.getWidg("maxSpin").set_visible(True)
            self.view.getWidg("delimiterEntry").set_visible(False)

            self.view.getWidg("factorLabel").set_visible(False)
            self.view.getWidg("factorEntry").set_visible(False)
            self.view.getWidg("offsetLabel").set_visible(False)
            self.view.getWidg("offsetEntry").set_visible(False)

            if handler_id is not None:
                object.disconnect(handler_id)
                handler_id = None

#===============================================================================
#        # Direct Relation variable
#        elif strVarType == DirectRelationVariable.TYPE:
#
#            self.view.getWidg("valueLabel").set_visible(False)
#            self.view.getWidg("typeLabel").set_visible(False)
#            self.view.getWidg("relationTypeLabel").set_visible(False)
#            self.view.getWidg("sizedLabel").set_visible(False)
#
#            self.view.getWidg("valueEntry").set_visible(False)
#            self.view.getWidg("typeCombo").set_visible(False)
#
#            self.view.getWidg("relationTypeCombo").set_visible(False)
#            self.view.getWidg("IDGrid").set_visible(True)
#            self.view.getWidg("IDLabel").set_visible(True)
#            self.view.getWidg("IDEntry").set_visible(True)
#            self.view.getWidg("IDButton").set_visible(True)
#            self.view.getWidg("sizedCheck").set_visible(False)
#
#            self.updateDelimiterAndSize(default=True)
#
#            if handler_id is not None:
#                object.disconnect(handler_id)
#                handler_id = None
#===============================================================================

        # Default case
        else:
            self.view.getWidg("valueLabel").set_visible(False)
            self.view.getWidg("typeLabel").set_visible(False)
            self.view.getWidg("relationTypeLabel").set_visible(False)
            self.view.getWidg("sizedLabel").set_visible(False)

            self.view.getWidg("valueEntry").set_visible(False)
            self.view.getWidg("typeCombo").set_visible(False)

            self.view.getWidg("relationTypeCombo").set_visible(False)
            self.view.getWidg("IDGrid").set_visible(False)
            self.view.getWidg("IDLabel").set_visible(False)
            self.view.getWidg("IDEntry").set_visible(False)
            self.view.getWidg("IDButton").set_visible(False)
            self.view.getWidg("sizedCheck").set_visible(False)

            self.view.getWidg("factorLabel").set_visible(False)
            self.view.getWidg("factorEntry").set_visible(False)
            self.view.getWidg("offsetLabel").set_visible(False)
            self.view.getWidg("offsetEntry").set_visible(False)

            self.updateDelimiterAndSize(default=True)

            if handler_id is not None:
                object.disconnect(handler_id)
                handler_id = None

    def updateDelimiterAndSize(self, widget=None, default=False):
        """updateDelimiterAndSize:
                Update the shown options (among min/max/deilmiter) of the variable creation view to set visible only those which are useful.
                For DataVariable and ComputedRelationVariable.
                Called by a toggling of the sizedCheck checkbox.

                @type widget: Gtk.widget
                @param widget: the widget which modification calls this function.
        """
        if self.view.getWidg("sizedCheck").get_active():
            self.view.getWidg("minLabel").set_visible(True)
            self.view.getWidg("maxLabel").set_visible(True)
            self.view.getWidg("delimiterLabel").set_visible(False)

            self.view.getWidg("minSpin").set_visible(True)
            self.view.getWidg("maxSpin").set_visible(True)
            self.view.getWidg("delimiterEntry").set_visible(False)
        else:
            self.view.getWidg("minLabel").set_visible(False)
            self.view.getWidg("maxLabel").set_visible(False)
            self.view.getWidg("delimiterLabel").set_visible(True)

            self.view.getWidg("minSpin").set_visible(False)
            self.view.getWidg("maxSpin").set_visible(False)
            self.view.getWidg("delimiterEntry").set_visible(True)

        if default:
            self.view.getWidg("minLabel").set_visible(False)
            self.view.getWidg("maxLabel").set_visible(False)
            self.view.getWidg("delimiterLabel").set_visible(False)

            self.view.getWidg("minSpin").set_visible(False)
            self.view.getWidg("maxSpin").set_visible(False)
            self.view.getWidg("delimiterEntry").set_visible(False)

    def updateMinSpin(self, widget):
        """updateMinSpin:
                Fix the value of minspin to len(value) in order to help the user to know the size of the value he entered.
        """
        size = len(str(self.view.getWidg("valueEntry").get_text()))
        # Protect previously defined minValue.
        # if self.view.getWidg("minSpin").get_text() is None or str(self.view.getWidg("minSpin").get_text()) == '' or size < int(self.view.getWidg("minSpin").get_text()):
        self.view.getWidg("minSpin").set_text(str(size))

    def updateMaxSpin(self, widget):
        """updateMaxSpin:
                Fix the value of maxSpin to at least minSpin.
                Called when minSpin is modified to a greater value than maxspin.
        """
        if self.view.getWidg("minSpin").get_text() is None or str(self.view.getWidg("minSpin").get_text()) == '':
            minSpin = 0
        else:
            minSpin = int(self.view.getWidg("minSpin").get_text())
        if self.view.getWidg("maxSpin").get_text() is None or str(self.view.getWidg("maxSpin").get_text()) == '':
            maxSpin = 0
        else:
            maxSpin = int(self.view.getWidg("maxSpin").get_text())
        if minSpin > maxSpin:
            self.view.getWidg("maxSpin").set_text(self.view.getWidg("minSpin").get_text())

    def runDialog(self):
        """runDialog:
                Run a dialog that allows to modify each definition field of a variable.
        """
        dialog = self.view.getWidg("dialog")
        dialog.show_all()

        # Edition of an existing variable.
        if self.editOverCreate:
            # We write the former values of the variable.
            self.view.getWidg("nameEntry").set_text(self.variable.getName())
            self.view.getWidg("mutableCheck").set_active(self.variable.isMutable())
            self.view.getWidg("learnableCheck").set_active(self.variable.isLearnable())
            self.view.getWidg("variableTypeCombo").set_active(VariableTreeController.VARIABLE_INDEX_LIST.index(self.variable.getVariableType()))

            # Data Variable
            if self.variable.getVariableType() == DataVariable.TYPE:
                if self.variable.getOriginalValue() is not None:
                    self.view.getWidg("valueEntry").set_text(self.variable.bin2str(self.variable.getOriginalValue()))
                else:
                    self.view.getWidg("valueEntry").set_text('')

                if self.variable.type.isSized():
                    self.view.getWidg("sizedCheck").set_active(True)
                    self.view.getWidg("minSpin").set_text(str(self.variable.getType().getMinChars()))
                    self.view.getWidg("maxSpin").set_text(str(self.variable.getType().getMaxChars()))
                    self.view.getWidg("delimiterEntry").set_text('')
                else:
                    self.view.getWidg("sizedCheck").set_active(False)
                    self.view.getWidg("minSpin").set_text('0')
                    self.view.getWidg("maxSpin").set_text('0')
                    self.view.getWidg("delimiterEntry").set_text(self.variable.bin2str(self.variable.getDelimiter()))

                self.view.getWidg("typeCombo").set_active(VariableTreeController.TYPE_INDEX_LIST.index(self.variable.getType().getType()))

            # Repeat Variable
            elif self.variable.getVariableType() == RepeatVariable.TYPE:
                self.view.getWidg("minSpin").set_text(str(self.variable.getNumberIterations()[0]))
                self.view.getWidg("maxSpin").set_text(str(self.variable.getNumberIterations()[1]))

            #===================================================================
            # # Direct Relation Variable
            # elif self.variable.getVariableType() == DirectRelationVariable.TYPE:
            #    self.view.getWidg("IDEntry").set_text(self.variable.getPointedVariable().getID())
            #===================================================================

            # Computed Relation Variable
            elif self.variable.getVariableType() == ComputedRelationVariable.TYPE:
                self.view.getWidg("IDEntry").set_text(self.variable.getPointedID())
                self.view.getWidg("relationTypeCombo").set_active(VariableTreeController.RELATION_TYPE_INDEX_LIST.index(self.variable.getRelationType().getType()))

                if self.variable.getRelationType().getAssociatedDataType().isSized():
                    self.view.getWidg("sizedCheck").set_active(True)
                    self.view.getWidg("minSpin").set_text(str(self.variable.getRelationType().getAssociatedDataType().getMinChars()))
                    self.view.getWidg("maxSpin").set_text(str(self.variable.getRelationType().getAssociatedDataType().getMaxChars()))
                    self.view.getWidg("delimiterEntry").set_text('')
                else:
                    self.view.getWidg("sizedCheck").set_active(False)
                    self.view.getWidg("minSpin").set_text('0')
                    self.view.getWidg("maxSpin").set_text('0')
                    self.view.getWidg("delimiterEntry").set_text(self.variable.bin2str(self.variable.getRelationType().getAssociatedDataType().getDelimiter()))

                self.view.getWidg("factorEntry").set_text(str(self.variable.getRelationType().getFactor()))
                self.view.getWidg("offsetEntry").set_text(str(self.variable.getRelationType().getOffset()))

        self.updateOptions()
        dialog.run()

    def validateChanges(self, widget):
        """validateChanges:
                Validate the changes that a user has done on a variable.
                Called by a click on the apply button.

                @type widget: Gtk.widget
                @param widget: the widget which calls this function.
        """

        dialog = self.view.getWidg("dialog")
        if self.editOverCreate:
            anid = self.variable.getID()
        else:
            anid = str(uuid.uuid4())

        name = self.view.getWidg("nameEntry").get_text()
        mutable = self.view.getWidg("mutableCheck").get_active()
        learnable = self.view.getWidg("learnableCheck").get_active()
        varTypeIndex = self.view.getWidg("variableTypeCombo").get_active()

        variable = None
        # Aggregate variable
        if varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(AggregateVariable.TYPE):
            variable = AggregateVariable(anid, name, mutable, learnable)

        # Alternate Variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(AlternateVariable.TYPE):
            variable = AlternateVariable(anid, name, mutable, learnable)

        # Repeat Variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(RepeatVariable.TYPE):
            minIterations = int(self.view.getWidg("minSpin").get_text())
            maxIterations = int(self.view.getWidg("maxSpin").get_text())
            variable = RepeatVariable(anid, name, mutable, learnable, None, minIterations, maxIterations)

        # Data Variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(DataVariable.TYPE):
            sized = self.view.getWidg("sizedCheck").get_active()
            if sized:
                # If the variable is defined by a size.
                minChars = int(self.view.getWidg("minSpin").get_text())
                maxChars = int(self.view.getWidg("maxSpin").get_text())
                delimiter = None
            else:
                # The variable is defined by a delimiter.
                minChars = 0
                maxChars = 0
                delimiter = self.view.getWidg("delimiterEntry").get_text()
            vtype = AbstractType.makeType(VariableTreeController.TYPE_INDEX_LIST[self.view.getWidg("typeCombo").get_active()], sized, minChars, maxChars, delimiter)
            originalValue = vtype.str2bin(self.view.getWidg("valueEntry").get_text())
            variable = DataVariable(anid, name, mutable, learnable, vtype, originalValue)

#===============================================================================
#        # Direct Relation Variable
#        elif strVarType == DirectRelationVariable.TYPE:
#
#            # We find the variable by its ID.
#            pointedID = str(self.view.getWidg("IDEntry").get_text())
#
#            variable = DirectRelationVariable(anid, name, mutable, learnable, pointedID, self.treeController.symbol)
#===============================================================================

        # Computed Relation Variable
        elif varTypeIndex == VariableTreeController.VARIABLE_INDEX_LIST.index(ComputedRelationVariable.TYPE):

            # We find the variable by its ID.
            pointedID = str(self.view.getWidg("IDEntry").get_text())

            sized = self.view.getWidg("sizedCheck").get_active()
            if sized:
                # If the variable is defined by a size.
                minChars = int(self.view.getWidg("minSpin").get_text())
                maxChars = int(self.view.getWidg("maxSpin").get_text())
                delimiter = None
            else:
                # The variable is defined by a delimiter.
                minChars = 0
                maxChars = 0
                delimiter = self.view.getWidg("delimiterEntry").get_text()

            factor = float(self.view.getWidg("factorEntry").get_text())
            offset = float(self.view.getWidg("offsetEntry").get_text())
            vtype = AbstractRelationType.makeType(VariableTreeController.RELATION_TYPE_INDEX_LIST[self.view.getWidg("relationTypeCombo").get_active()], sized, minChars, maxChars, delimiter, factor, offset)
            variable = ComputedRelationVariable(anid, name, mutable, learnable, vtype, pointedID, self.treeController.symbol)

        if variable is not None:
            # This part is for saving and transfering children when transforming a node variable into an other kind of node variable.
            if self.editOverCreate:
                father = None
                if len(self.variable.getFathers()) > 0:
                    father = self.variable.getFathers()[0]
                # We transform a node variable into a node variable.
                if (self.variable.getVariableType() == AggregateVariable.TYPE or self.variable.getVariableType() == AlternateVariable.TYPE) and (variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE):
                    children = self.variable.getChildren()
                    self.variable = variable
                    for child in children:
                        self.variable.addChild(child)

                # We transform a repeat variable into a node variable.
                elif (self.variable.getVariableType() == RepeatVariable.TYPE) and (variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE):
                    child = self.variable.getChild()
                    self.variable = variable
                    self.variable.addChild(child)

                # We transform a repeat variable into a repeat variable.
                elif (self.variable.getVariableType() == RepeatVariable.TYPE) and (variable.getVariableType() == RepeatVariable.TYPE):
                    child = self.variable.getChild()
                    self.variable = variable
                    self.variable.setChild(child)

                # We do not manage/save children.
                else:
                    self.variable = variable
                if father is not None:
                    self.variable.addFather(father)
                self.treeController.editVariable(self.variable)

            else:
                if self.variable.getVariableType() == RepeatVariable.TYPE:
                    self.variable.setChild(variable)
                else:
                    self.variable.addChild(variable)
                self.treeController.registerVariable(self.rootEntry, variable)
        dialog.destroy()

    def chooseSelectedVariable(self, widget):
        """chooseSelectedVariable:
                Manage the creation and showing of a VariableIDTreeController that allows the user to choose one variable and get its ID.

                @param widget: the widget which is connected to this function through the event event.
        """
        VariableIDTreeController(self)


class VariableMovingController(object):
    """VariableMovingController:
            Manage a view that allows the user to move a variable to a specified position.
    """

    def __init__(self, item, treeController, variable):
        """Constructor of VariableMovingController:
                Called by a click on the tree view of all variables.

                @type item: Gtk.Menuitem
                @param item: the menu item that calls this constructor.
                @type treeController: VariableTreeController
                @param treeController: the controller of the tree view which cause this controller's view to appear.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable
                @param variable: the variable that will be modified/to which we will add a child.
        """
        self.treeController = treeController
        self.netzob = self.treeController.netzob
        self.variable = variable
        self.view = VariableMovingView(self)
        self.initCallBacks()
        self.runDialog()

    def initCallBacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("applyButton").connect("clicked", self.validateChanges)

    def runDialog(self):
        """runDialog:
                Run a dialog that allows to move a variable.
        """
        dialog = self.view.getWidg("dialog")
        self.view.getWidg("entry").set_text(str(self.variable.getFathers()[0].indexOfChild(self.variable)))
        dialog.show_all()
        dialog.run()

    def validateChanges(self, widget):
        """validateChanges:
                Validate the changes that a user has done on a variable.
                Called by a click on the apply button.

                @type widget: Gtk.widget
                @param widget: the widget which calls this function.
        """
        position = int(self.view.getWidg("entry").get_text())

        # Move the variable entry in the tree view.
        entry = self.treeController.dictEntry[self.variable.getID()]
        self.treeController.treestore.move_before(entry, self.treeController.dictEntry[self.variable.getFathers()[0].getChildren()[position].getID()])

        # Move the variable.
        self.variable.getFathers()[0].moveChild(self.variable, position)

        self.view.getWidg("dialog").destroy()


class VariableIDTreeController(object):
    """VariableIDTreeController:
            Controls a variable's ID tree view display.
            This treeview displays every variable of the vocabulary and is useful for selecting one of them.
    """

    def __init__(self, variableCreationController):
        """Constructor of VariableIDTreeController:

                @type variableCreationController: VariableCreationController
                @param variableCreationController: the variable creation controller that indirectly causes this variableIDTreeController to appear.
        """
        self.view = VariableTreeView(self)
        self.netzob = variableCreationController.netzob
        self.variableCreationController = variableCreationController
        self.registerContent()
        self.selectedVariable = None
        self.view.getWidg("createDefaultVariable_button").set_visible(False)

    def initCallbacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.view.getWidg("treeview").connect('button-press-event', self.clickOnElement)
        self.view.getWidg("button").connect('clicked', self.selectElement)

    def registerContent(self):
        """registerContent:
                Register each variable and their entry in the tree view.
                Fill the tree view of a variable with all its displayable content.
        """
        self.dictEntry = dict()
        self.dictVariable = dict()
        self.treestore = Gtk.TreeStore(str, str)  # id of the data, description
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            self.registerVariable(None, symbol.getRoot())
        self.initCallbacks()
        self.view.getWidg("treeview").set_model(self.treestore)

    def registerVariable(self, rootEntry, variable):
        """registerVariable:
                Register a variable in the tree view under its root variable (Aggregate or Alternate).
                May be recursive.

                @type rootEntry: Gtk.treerow
                @param rootEntry: the root entry under which we will add this entry.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the variable which will be added to the tree view representation.
        """
        self.dictVariable[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), variable.toString()])
        self.dictEntry[str(variable.getID())] = newEntry
        if variable.getVariableType() == AggregateVariable.TYPE or variable.getVariableType() == AlternateVariable.TYPE:
            if variable.getChildren() is not None:
                for child in variable.getChildren():
                    self.registerVariable(newEntry, child)
        if variable.getVariableType() == RepeatVariable.TYPE:
            if variable.getChild() is not None:
                self.registerVariable(newEntry, variable.getChild())

    def clickOnElement(self, treeview, event):
        """clickOnElement:
                Called on click on a variable.

                @param treeview: the treeview which contains the triggering variable.
                @param event: the mouse event which called this function.
        """
        if event.button == 1:  # left click
            try:
                x = int(event.x)
                y = int(event.y)
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

                # Retrieve the selected variable
                varid = None
                aniter = treeview.get_model().get_iter(path)
                if aniter:
                    if treeview.get_model().iter_is_valid(aniter):
                        varid = treeview.get_model().get_value(aniter, 0)

                        if varid is not None:
                            self.selectedVariable = self.dictVariable[varid]
            except:
                logging.debug(_("The user clicks on no variable."))
        else:
            # Wrong mouse click
            return

    def selectElement(self, widget):
        """selectElement:
                Give the ID of the variable associated to the selected element to the globally calling variableCreationController.

                @param widget: the widget on which this function is connected.
        """
        if self.selectedVariable is not None:
            self.variableCreationController.view.getWidg("IDEntry").set_text(str(self.selectedVariable.getID()))
            self.view.getWidg("dialog").destroy()
        else:
            NetzobErrorMessage(_("No variable selected."))
