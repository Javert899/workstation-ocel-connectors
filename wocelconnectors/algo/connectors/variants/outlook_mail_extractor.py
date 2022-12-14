from typing import Optional, Dict
from wocelconnectors.algo.connectors.util import mail as mail_utils
import pandas as pd
from datetime import datetime
from typing import List, Any
import pkgutil
import traceback


correspondence = {
    "43": "Mail",
    "53": "Meeting Request",
    "54": "Meeting Cancellation",
    "55": "Meeting Declination",
    "56": "Meeting Acceptance",
    "57": "Meeting Tentatively Accepted",
    "181": "Meeting Forward Notification",
    "46": "Delivery Report"
}


def get_events(box, prefix, progress) -> List[Dict[str, Any]]:
    """
    Utility method extracting the items of a given mailbox.

    Parameters
    --------------
    box
        Mailbox
    prefix
        Prefix for the activities (Sent / Received )

    Returns
    --------------
    list_events
        List of events (dictionaries)
    """
    events = []
    for it in box.Items:
        cla = " "
        try:
            cla = str(it.Class)
            if cla in correspondence:
                cla = prefix + correspondence[cla]
                subject = str(it.Subject)
                timestamp = datetime.fromtimestamp(it.CreationTime.timestamp())
                sender = "EMPTY"
                try:
                    sender = str(it.Sender.Name)
                except:
                    pass
                recipients = "EMPTY"
                try:
                    recipients = " AND ".join([str(x.Name) for x in it.Recipients])
                except:
                    pass
                conversationid = str(it.ConversationID)
                conversationtopic = str(it.ConversationTopic)
                events.append({"case:concept:name": conversationid, "concept:name": cla, "time:timestamp": timestamp,
                               "org:resource": sender, "recipients": recipients, "topic": conversationtopic, "subject": subject})
        except:
            traceback.print_exc()
            pass
        if progress is not None:
            progress.update()
    return events


def apply(parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Extracts the history of the conversations from the local instance of Microsoft Outlook
    running on the current computer.

    CASE ID (case:concept:name) => identifier of the conversation
    ACTIVITY (concept:name) => activity that is performed in the current item (send e-mail, receive e-mail, refuse meeting ...)
    TIMESTAMP (time:timestamp) => timestamp of creation of the item in Outlook
    RESOURCE (org:resource) => sender of the current item

    Returns
    ---------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    inbox = mail_utils.connect(None, 6)
    outbox = mail_utils.connect(None, 5)

    progress = None
    if pkgutil.find_loader("tqdm"):
        from tqdm.auto import tqdm
        progress = tqdm(total=len(outbox.Items)+len(inbox.Items),
                        desc="extracting mailbox items, progress :: ")

    events = get_events(outbox, "Sent ", progress)
    events = events + get_events(inbox, "Received ", progress)

    if progress is not None:
        progress.close()

    dataframe = pd.DataFrame(events)
    dataframe["@@index"] = dataframe.index
    dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
    dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
    dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])

    return dataframe
