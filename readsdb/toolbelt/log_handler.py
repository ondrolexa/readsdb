#! python3  # noqa: E265

# standard library
import logging
from collections.abc import Callable
from functools import partial

# PyQGIS
from qgis.core import Qgis, QgsMessageLog, QgsMessageOutput
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QPushButton, QWidget
from qgis.utils import iface

# project package
import readsdb.toolbelt.preferences as plg_prefs_hdlr
from readsdb.__about__ import __title__

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgLogger(logging.Handler):
    """Python logging handler supercharged with QGIS useful methods."""

    @staticmethod
    def log(
        message: str,
        application: str = __title__,
        log_level: Qgis.MessageLevel = Qgis.MessageLevel.Info,
        push: bool = False,
        duration: int | None = None,
        # widget
        button: bool = False,
        button_text: str | None = None,
        button_more_text: str | None = None,
        button_connect: Callable | None = None,
        # parent
        parent_location: QWidget | None = None,
    ):
        """Send messages to QGIS messages windows and to the user as a message bar. \
        Plugin name is used as title. If debug mode is disabled, only warnings and \
        errors or with push are sent.

        :param message: message to display
        :type message: str
        :param application: name of the application sending the message. \
        Defaults to __about__.__title__
        :type application: str, optional
        :param log_level: message level. Possible values: any values of enum \
            `Qgis.MessageLevel`. Defaults to Qgis.MessageLevel.INFO
        :type log_level: Qgis.MessageLevel, optional
        :param push: also display the message in the QGIS message bar in addition to \
        the log, defaults to False
        :type push: bool, optional
        :param duration: duration of the message in seconds. If not set, the \
        duration is calculated from the log level: `(log_level + 1) * 3`. seconds. \
        If set to 0, then the message must be manually dismissed by the user. \
        Defaults to None.
        :type duration: int, optional
        :param button: display a button in the message bar. Defaults to False.
        :type button: bool, optional
        :param button_text: text label of the button. Defaults to None.
        :type button_text: str, optional
        :param button_more_text: text to display within the QgsMessageOutput
        :type button_more_text: str, optional
        :param button_connect: function to be called when the button is pressed. \
        If not set, a simple dialog (QgsMessageOutput) is used to dislay the message. \
        Defaults to None.
        :type button_connect: Callable, optional
        :param parent_location: parent location widget. \
        If not set, QGIS canvas message bar is used to push message, \
        otherwise if a QgsMessageBar is available in parent_location it is used instead. \
        Defaults to None.
        :type parent_location: Widget, optional

        :Example:

        .. code-block:: python

            # using enums from Qgis:
            # Qgis.MessageLevel.Info, Qgis.MessageLevel.Warning, Qgis.MessageLevel.Critical, Qgis.MessageLevel.Success, Qgis.MessageLevel.NoLevel
            from qgis.core import Qgis

            log(message="Plugin loaded - INFO", log_level=Qgis.MessageLevel.Info, push=False)
            log(
                message="Something went wrong but it's not blocking",
                log_level=Qgis.MessageLevel.Warning
            )
            log(
                message="Plugin failed to load - CRITICAL",
                log_level=Qgis.MessageLevel.Critical,
                push=True
            )

            # LEGACY - using integers:
            log(message="Plugin loaded - INFO", log_level=Qgis.MessageLevel.Info, push=False)
            log(message="Plugin loaded - WARNING", log_level=Qgis.MessageLevel.Warning, push=1, duration=5)
            log(message="Plugin loaded - ERROR", log_level=Qgis.MessageLevel.Critical, push=1, duration=0)
            log(
                message="Plugin loaded - SUCCESS",
                log_level=Qgis.MessageLevel.Success,
                push=1,
                duration=10,
                button=True
            )
            log(
                message="Plugin loaded",
                log_level=Qgis.MessageLevel.Critical,
                push=1,
                duration=0
                button=True,
                button_label=self.tr("See details"),
                button_more_text=detailed_error_message
            )
            log(message="Plugin loaded - TEST", log_level=Qgis.MessageLevel.NoLevel, push=0)
        """
        # if not debug mode and not push, let's ignore INFO, SUCCESS and TEST
        debug_mode = plg_prefs_hdlr.PlgOptionsManager.get_plg_settings().debug_mode
        if (
            not debug_mode
            and not push
            and (
                log_level < Qgis.MessageLevel.Warning
                or log_level > Qgis.MessageLevel.Critical
            )
        ):
            return

        # ensure message is a string
        if not isinstance(message, str):
            try:
                message = str(message)
            except Exception as err:
                err_msg = "Log message must be a string, not: {}. Trace: {}".format(
                    type(message), err
                )
                logging.error(err_msg)
                message = err_msg

        # send it to QGIS messages panel
        QgsMessageLog.logMessage(
            message=message, tag=application, notifyUser=push, level=log_level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push and iface is not None:
            msg_bar = None

            # QGIS or custom dialog
            if parent_location and isinstance(parent_location, QWidget):
                msg_bar = parent_location.findChild(QgsMessageBar)

            if not msg_bar:
                msg_bar = iface.messageBar()

            # calc duration
            if duration is None:
                duration = (int(log_level) + 1) * 3

            # create message with/out a widget
            if button:
                # create output message
                notification = iface.messageBar().createMessage(
                    title=application, text=message
                )
                widget_button = QPushButton(button_text or "More...")
                if button_connect:
                    widget_button.clicked.connect(button_connect)
                else:
                    mini_dlg: QgsMessageOutput = QgsMessageOutput.createMessageOutput()
                    mini_dlg.setTitle(application)
                    mini_dlg.setMessage(
                        f"{message}\n{button_more_text}",
                        QgsMessageOutput.MessageType.MessageText,
                    )
                    widget_button.clicked.connect(partial(mini_dlg.showMessage, False))

                notification.layout().addWidget(widget_button)
                msg_bar.pushWidget(
                    widget=notification, level=log_level, duration=duration
                )

            else:
                # send simple message
                msg_bar.pushMessage(
                    title=application,
                    text=message,
                    level=log_level,
                    duration=duration,
                )
