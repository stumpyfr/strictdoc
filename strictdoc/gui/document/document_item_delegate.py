import re

import PySide2
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import (QAbstractTextDocumentLayout)
from PySide2.QtWidgets import (QApplication,
                               QStyledItemDelegate,
                               QStyleOptionViewItem,
                               QStyle)

from strictdoc.gui.document.document_item_editor import DocumentItemEditor
from strictdoc.gui.document.document_node import DocumentNode, DOCUMENT_MARGIN

MAGIC_VALUE = 18


class DocumentItemDelegate(QStyledItemDelegate):
    table_view = None
    current_editor = None
    current_edited_index = None
    document_nodes = {}

    def __init__(self):
        QStyledItemDelegate.__init__(self)

    # How to make a fast QTableView with HTML-formatted and clickable cells?
    # https://stackoverflow.com/a/44365155/598057
    # How to make item view render rich (html) text in Qt
    # https://stackoverflow.com/a/5443112/598057
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        print("paint: {} {} {}".format(index, options, options.text[0:6]))

        style = options.widget.style() if options.widget else QApplication.style()

        assert index in self.document_nodes
        document_node = self.document_nodes[index]

        options.text = ''
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, options)

        painter.save()

        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        # painter.translate(0, 0.5*(options.rect.height() - doc.size().height()))

        document_node.get_document().documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        print("--- sizeHint ---")
        print("sizeHint/index: {} {}".format(index, option))
        print("sizeHint/row/column: {} / {}".format(index.row(), index.column()))

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        widget = options.widget

        # TODO: This is ugly hack. Somehow the real streched cell's width has
        # TODO: to be found.
        estimated_width = widget.width() - MAGIC_VALUE

        if index not in self.document_nodes:
            self.document_nodes[index] = DocumentNode(options.text, estimated_width)
        document_node = self.document_nodes[index]

        # If this is an active cell, we make sure it is resized according to
        # what's being edited.
        if self.current_editor and index == self.current_edited_index:
            clone = document_node.get_document_clone(self.current_editor.toPlainText())

            size = QSize(int(clone.size().width()), int(clone.size().height()))
            print("estimated clone size: {}".format(size))
            return size

        document_node.update_text(options.text)

        doc = document_node.get_document()

        size = QSize(int(doc.size().width()), int(doc.size().height()))
        print("document_node doc size: {}".format(size))

        return size

    def createEditor(self, parent, option, index):
        print("--- createEditor: parent: {}".format(parent))
        assert index.column() == 0

        textedit = DocumentItemEditor(parent)
        textedit.document().setDocumentMargin(DOCUMENT_MARGIN)
        textedit.setLineWrapMode(PySide2.QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        textedit.editingFinished.connect(self.text_finished)

        self.current_editor = textedit
        self.current_edited_index = index

        return textedit

    def setEditorData(self, editor, index):
        assert isinstance(editor, DocumentItemEditor)

        print("--- setEditorData")
        text_value = index.model().get_item_as_rst(index)
        print("textValue: {}".format(text_value))

        editor.setPlainText(text_value)

        self.table_view.resizeRowsToContents()
        editor.textChanged.connect(self.text_changed)

    def setModelData(self, editor, model, index):
        # TODO: Why this method if there is a working DocumentModel.setData?
        # super().setModelData(editor, model, index)

        stripped_text = re.sub(r'\n+', '\n', editor.toPlainText())
        index.model().set_item_from_rst(index, stripped_text.strip())

    def text_changed(self):
        assert self.current_editor

        document_node = self.document_nodes[self.current_edited_index]
        document_node.update_text(self.current_editor.toPlainText())

        size = self.current_editor.document().size().toSize()
        self.current_editor.setFixedHeight(size.height())

        # It is important that we notify table view to update the cells because
        # here it seems to be the right (and only) place to do so.
        self.table_view.resizeRowsToContents()

    def text_finished(self):
        self.current_editor = None
        self.current_edited_index = None

        self.table_view.resizeRowsToContents()