import logging
from systemd.journal import JournalHandler

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

log.info("This message will be sent to systemd's journal")
