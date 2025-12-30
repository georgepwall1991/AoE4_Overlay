import sys
from unittest.mock import MagicMock


def setup_pyqt_mocks():
    if 'PyQt5' in sys.modules and not isinstance(sys.modules['PyQt5'], MagicMock):
        # Already imported real PyQt5? (unlikely here)
        return

    # Base classes that might be inherited from
    class MockQWidget:
        def __init__(self, *args, **kwargs):
            pass

        def setWindowFlags(self, *args, **kwargs):
            pass

        def setAttribute(self, *args, **kwargs):
            pass

        def setLayout(self, *args, **kwargs):
            pass

        def setStyleSheet(self, style=""):
            self._stylesheet = style

        def styleSheet(self):
            return getattr(self, '_stylesheet', "")

        def setGeometry(self, *args, **kwargs):
            pass

        def move(self, *args, **kwargs):
            pass

        def show(self, *args, **kwargs):
            pass

        def hide(self, *args, **kwargs):
            pass

        def isVisible(self):
            return True

        def width(self):
            return 100

        def height(self):
            return 100

        def pos(self):
            mock_pos = MagicMock()
            mock_pos.x.return_value = 0
            mock_pos.y.return_value = 0
            return mock_pos

        def x(self):
            return 0

        def y(self):
            return 0

        def setAlignment(self, *args, **kwargs):
            pass

        def setContentsMargins(self, *args, **kwargs):
            pass

        def setFixedSize(self, *args, **kwargs):
            pass

        def setScaledContents(self, *args, **kwargs):
            pass

        def setObjectName(self, *args, **kwargs):
            pass

        def addWidget(self, *args, **kwargs):
            pass

        def parent(self):
            return MagicMock()

        def close(self):
            pass

        def setWindowTitle(self, *args, **kwargs):
            pass

        def setMinimumWidth(self, *args, **kwargs):
            pass

        def setMinimumHeight(self, *args, **kwargs):
            pass

        def setMaximumWidth(self, *args, **kwargs):
            pass

        def setMaximumHeight(self, *args, **kwargs):
            pass

        def setMinimumSize(self, *args, **kwargs):
            pass

        def setMaximumSize(self, *args, **kwargs):
            pass

        def setSizePolicy(self, *args, **kwargs):
            pass

        def setWindowOpacity(self, opacity):
            self._opacity = opacity

        def windowOpacity(self):
            return getattr(self, '_opacity', 1.0)

        def activateWindow(self):
            pass

        def raise_(self):
            pass

        def lower(self):
            pass

        def resize(self, *args, **kwargs):
            pass

        def size(self):
            mock_size = MagicMock()
            mock_size.width.return_value = 100
            mock_size.height.return_value = 100
            return mock_size

        def update(self):
            pass

        def repaint(self):
            pass

        def deleteLater(self):
            pass

        def setFocus(self):
            pass

        def clearFocus(self):
            pass

        def hasFocus(self):
            return False

        def setEnabled(self, enabled):
            self._enabled = enabled

        def isEnabled(self):
            return getattr(self, '_enabled', True)

        def setVisible(self, visible):
            self._visible = visible

        def grabKeyboard(self):
            pass

        def releaseKeyboard(self):
            pass

        def installEventFilter(self, *args):
            pass

        def removeEventFilter(self, *args):
            pass

        def setToolTip(self, *args, **kwargs):
            pass

        def toolTip(self):
            return ""

        def setWhatsThis(self, *args, **kwargs):
            pass

        def setCursor(self, *args, **kwargs):
            pass

        def setFont(self, *args, **kwargs):
            pass

        def font(self):
            return MagicMock()

        def setFocusPolicy(self, *args, **kwargs):
            pass

        def setContextMenuPolicy(self, *args, **kwargs):
            pass

        def setAcceptDrops(self, *args, **kwargs):
            pass

        def setPalette(self, *args, **kwargs):
            pass

        def palette(self):
            return MagicMock()

        def setAutoFillBackground(self, *args, **kwargs):
            pass

        def setMouseTracking(self, *args, **kwargs):
            pass

        def underMouse(self):
            return False

        def mapToGlobal(self, point):
            return point

        def mapFromGlobal(self, point):
            return point

        def geometry(self):
            mock_geom = MagicMock()
            mock_geom.x.return_value = 0
            mock_geom.y.return_value = 0
            mock_geom.width.return_value = 100
            mock_geom.height.return_value = 100
            return mock_geom

        def rect(self):
            mock_rect = MagicMock()
            mock_rect.width.return_value = 100
            mock_rect.height.return_value = 100
            return mock_rect

        def frameGeometry(self):
            return self.geometry()

        def sizeHint(self):
            mock_size = MagicMock()
            mock_size.width.return_value = 100
            mock_size.height.return_value = 100
            return mock_size

    class MockQAbstractTableModel:
        def __init__(self, *args, **kwargs):
            pass

        def beginResetModel(self):
            pass

        def endResetModel(self):
            pass

        def beginInsertRows(self, *args):
            pass

        def endInsertRows(self):
            pass

        def index(self, *args):
            return MagicMock()

        def rowCount(self, *args):
            return 0

        def columnCount(self, *args):
            return 0

        def data(self, *args):
            return None

        def headerData(self, *args):
            return None

    class MockQObject:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, *args):
            pass

        def emit(self, *args):
            pass

    class MockQRunnable:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    class MockSignal:
        """A mock signal that works like pyqtSignal"""
        def __init__(self, *args):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def disconnect(self, callback=None):
            if callback:
                self._callbacks = [c for c in self._callbacks if c != callback]
            else:
                self._callbacks = []

        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception:
                    pass

    def pyqt_signal_factory(*args):
        """Factory that returns a MockSignal instance descriptor"""
        return MockSignal(*args)

    class MockQLabel(MockQWidget):
        def __init__(self, text="", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._text = str(text) if text else ""
            self._pixmap = None

        def setText(self, text):
            self._text = text

        def text(self):
            return self._text

        def setPixmap(self, pixmap):
            self._pixmap = pixmap

        def pixmap(self):
            return self._pixmap

        def setOpenExternalLinks(self, *args, **kwargs):
            pass

        def setWordWrap(self, *args, **kwargs):
            pass

        def setTextFormat(self, *args, **kwargs):
            pass

        def setTextInteractionFlags(self, *args, **kwargs):
            pass

        def setBuddy(self, *args, **kwargs):
            pass

        def setIndent(self, *args, **kwargs):
            pass

        def setMargin(self, *args, **kwargs):
            pass

        def adjustSize(self, *args, **kwargs):
            pass

    class MockQLineEdit(MockQWidget):
        textChanged = MockSignal(str)

        def __init__(self, text="", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._text = text
            self.textChanged = MockSignal(str)

        def setText(self, text):
            self._text = text

        def text(self):
            return self._text

        def setTextMargins(self, *args, **kwargs):
            pass

        def setPlaceholderText(self, *args, **kwargs):
            pass

        def setReadOnly(self, *args, **kwargs):
            pass

        def selectAll(self):
            pass

        def clear(self):
            self._text = ""

    class MockQComboBox(MockQWidget):
        currentIndexChanged = MockSignal(int)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._items = []
            self._current_index = 0
            self._current_text = ""
            self.currentIndexChanged = MockSignal(int)

        def addItem(self, text, data=None):
            self._items.append((text, data))
            if not self._current_text:
                self._current_text = text

        def setItemIcon(self, index, icon):
            pass

        def currentText(self):
            return self._current_text

        def setCurrentText(self, text):
            self._current_text = text

        def currentIndex(self):
            return self._current_index

        def setCurrentIndex(self, index):
            self._current_index = index

    class MockQCheckBox(MockQWidget):
        stateChanged = MockSignal(int)

        def __init__(self, text="", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._checked = False
            self.stateChanged = MockSignal(int)

        def isChecked(self):
            return self._checked

        def setChecked(self, checked):
            self._checked = checked

    class MockQPushButton(MockQWidget):
        clicked = MockSignal()

        def __init__(self, text="", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._text = text
            self.clicked = MockSignal()

        def setMaximumWidth(self, width):
            pass

        def setShortcut(self, shortcut):
            pass

    class MockQGridLayout:
        def __init__(self, *args, **kwargs):
            pass

        def addWidget(self, *args, **kwargs):
            pass

        def addItem(self, *args, **kwargs):
            pass

        def setContentsMargins(self, *args, **kwargs):
            pass

        def setHorizontalSpacing(self, *args, **kwargs):
            pass

        def setAlignment(self, *args, **kwargs):
            pass

        def addLayout(self, *args, **kwargs):
            pass

        def addStretch(self, *args, **kwargs):
            pass

        def addSpacing(self, *args, **kwargs):
            pass

        def setVerticalSpacing(self, *args, **kwargs):
            pass

        def setRowStretch(self, *args, **kwargs):
            pass

        def setColumnStretch(self, *args, **kwargs):
            pass

        def count(self):
            return 0

        def itemAt(self, index):
            return MagicMock()

        def takeAt(self, index):
            return MagicMock()

    class MockQVBoxLayout(MockQGridLayout):
        def setSpacing(self, *args, **kwargs):
            pass

    class MockQHBoxLayout(MockQGridLayout):
        pass

    class MockQSpacerItem:
        def __init__(self, *args, **kwargs):
            pass

    class MockQFrame(MockQWidget):
        pass

    class MockQMainWindow(MockQWidget):
        def setCentralWidget(self, *args, **kwargs):
            pass

        def centralWidget(self):
            return MagicMock()

        def menuBar(self):
            return MagicMock()

        def statusBar(self):
            return MagicMock()

    class MockQDialog(MockQWidget):
        def exec_(self):
            return 0

        def accept(self):
            pass

        def reject(self):
            pass

    class MockQScrollArea(MockQWidget):
        def setWidget(self, *args, **kwargs):
            pass

        def setWidgetResizable(self, *args, **kwargs):
            pass

        def widget(self):
            return MagicMock()

    class MockQTabWidget(MockQWidget):
        def addTab(self, *args, **kwargs):
            pass

    class MockQTableView(MockQWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.clicked = MockSignal()

        def setModel(self, *args):
            pass

        def horizontalHeader(self):
            header = MagicMock()
            header.setSectionResizeMode = MagicMock()
            return header

        def verticalHeader(self):
            header = MagicMock()
            header.setVisible = MagicMock()
            return header

        def setSelectionBehavior(self, *args):
            pass

        def setSelectionMode(self, *args):
            pass

        def alternatingRowColors(self):
            return False

        def setShowGrid(self, *args):
            pass

        def setWordWrap(self, *args):
            pass

        def resizeRowsToContents(self):
            pass

        def setAlternatingRowColors(self, *args):
            pass

    class MockQDesktopWidget(MockQWidget):
        def screenGeometry(self, screen=0):
            mock_geom = MagicMock()
            mock_geom.width.return_value = 1920
            mock_geom.height.return_value = 1080
            mock_geom.top.return_value = 0
            return mock_geom

    class MockQKeySequenceEdit(MockQWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._sequence = ""

        def keySequence(self):
            mock_seq = MagicMock()
            mock_seq.toString.return_value = self._sequence
            return mock_seq

        def setKeySequence(self, seq):
            pass

    class MockQModelIndex:
        def __init__(self):
            pass

        def isValid(self):
            return True

        def row(self):
            return 0

        def column(self):
            return 0

    # Create module mocks with real classes
    class QtCoreModule:
        QObject = MockQObject
        Qt = MagicMock()
        QAbstractTableModel = MockQAbstractTableModel
        QRunnable = MockQRunnable
        QThreadPool = MagicMock
        QPoint = MagicMock
        QSize = MagicMock
        QRect = MagicMock
        QModelIndex = MockQModelIndex
        pyqtSignal = pyqt_signal_factory
        pyqtSlot = lambda *args: (lambda f: f)

    # Set Qt constants
    QtCoreModule.Qt.DisplayRole = 0
    QtCoreModule.Qt.AlignCenter = 4
    QtCoreModule.Qt.AlignVCenter = 128
    QtCoreModule.Qt.AlignRight = 2
    QtCoreModule.Qt.AlignLeft = 1
    QtCoreModule.Qt.AlignTop = 32
    QtCoreModule.Qt.KeepAspectRatio = 1
    QtCoreModule.Qt.SmoothTransformation = 1
    QtCoreModule.Qt.FramelessWindowHint = 1
    QtCoreModule.Qt.WindowTransparentForInput = 1
    QtCoreModule.Qt.WindowStaysOnTopHint = 1
    QtCoreModule.Qt.CoverWindow = 1
    QtCoreModule.Qt.NoDropShadowWindowHint = 1
    QtCoreModule.Qt.WindowDoesNotAcceptFocus = 1
    QtCoreModule.Qt.WA_TranslucentBackground = 1
    QtCoreModule.Qt.Window = 1
    QtCoreModule.Qt.CustomizeWindowHint = 1
    QtCoreModule.Qt.WindowTitleHint = 1
    QtCoreModule.Qt.Horizontal = 1
    QtCoreModule.Qt.TextAlignmentRole = 7
    QtCoreModule.Qt.ForegroundRole = 9
    QtCoreModule.Qt.FontRole = 6

    class QtGuiModule:
        QPixmap = MagicMock(return_value=MagicMock())
        QIcon = MagicMock(return_value=MagicMock())
        QFont = MagicMock(return_value=MagicMock())
        QColor = MagicMock(return_value=MagicMock())
        QPainter = MagicMock(return_value=MagicMock())
        QKeySequence = MagicMock(return_value=MagicMock())
        QMouseEvent = MagicMock

    class QtWidgetsModule:
        QWidget = MockQWidget
        QLabel = MockQLabel
        QLineEdit = MockQLineEdit
        QComboBox = MockQComboBox
        QCheckBox = MockQCheckBox
        QPushButton = MockQPushButton
        QFrame = MockQFrame
        QGridLayout = MockQGridLayout
        QVBoxLayout = MockQVBoxLayout
        QHBoxLayout = MockQHBoxLayout
        QTabWidget = MockQTabWidget
        QTableView = MockQTableView
        QHeaderView = MagicMock()
        QAbstractItemView = MagicMock()
        QScrollArea = MockQScrollArea
        QDesktopWidget = MockQDesktopWidget
        QKeySequenceEdit = MockQKeySequenceEdit
        QApplication = MagicMock()
        QSpacerItem = MockQSpacerItem
        QMainWindow = MockQMainWindow
        QDialog = MockQDialog
        QSizePolicy = MagicMock()
        QFormLayout = MockQGridLayout
        QSlider = MagicMock()
        QSpinBox = MagicMock()
        QTextEdit = MagicMock()
        QListWidget = MagicMock()
        QListWidgetItem = MagicMock()
        QMenu = MagicMock()
        QAction = MagicMock()
        QFileDialog = MagicMock()
        QMessageBox = MagicMock()
        QColorDialog = MagicMock()
        QSplitter = MagicMock()
        QGroupBox = MockQWidget
        QRadioButton = MockQWidget
        QStackedWidget = MockQWidget
        QToolButton = MockQWidget
        QShortcut = MagicMock()

    # Set header resize modes
    QtWidgetsModule.QHeaderView.Stretch = 1
    QtWidgetsModule.QHeaderView.ResizeToContents = 2
    QtWidgetsModule.QAbstractItemView.SelectRows = 1
    QtWidgetsModule.QAbstractItemView.SingleSelection = 1

    # Register modules - IMPORTANT: The PyQt5 mock must have our module classes
    # as attributes so that `from PyQt5 import QtCore` works correctly
    pyqt5_mock = MagicMock()
    pyqt5_mock.QtCore = QtCoreModule
    pyqt5_mock.QtGui = QtGuiModule
    pyqt5_mock.QtWidgets = QtWidgetsModule

    sys.modules['PyQt5'] = pyqt5_mock
    sys.modules['PyQt5.QtCore'] = QtCoreModule
    sys.modules['PyQt5.QtGui'] = QtGuiModule
    sys.modules['PyQt5.QtWidgets'] = QtWidgetsModule
