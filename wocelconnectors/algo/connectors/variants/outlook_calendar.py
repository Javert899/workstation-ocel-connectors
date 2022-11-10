from typing import Optional, Dict, Any
from pm4py.util import exec_utils
from enum import Enum
from wocelconnectors.algo.connectors.util import mail as mail_utils
import pandas as pd
from datetime import datetime
import pkgutil


class Parameters(Enum):
    EMAIL_USER = "email_user"
    CALENDAR_ID = "calendar_id"


def apply(parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Extracts the history of the calendar events (creation, update, start, end)
    in a Pandas dataframe from the local Outlook instance running on the current computer.

    CASE ID (case:concept:name) => identifier of the meeting
    ACTIVITY (concept:name) => one between: Meeting Created, Last Change of Meeting, Meeting Started, Meeting Completed
    TIMESTAMP (time:timestamp) => the timestamp of the event
    case:subject => the subject of the meeting

    Returns
    -------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    calendar_id = exec_utils.get_param_value(Parameters.CALENDAR_ID, parameters, 9)
    email_user = exec_utils.get_param_value(Parameters.EMAIL_USER, parameters, None)

    calendar = mail_utils.connect(email_user, calendar_id)

    progress = None
    if pkgutil.find_loader("tqdm"):
        from tqdm.auto import tqdm
        progress = tqdm(total=len(calendar.Items),
                        desc="extracting calendar items, progress :: ")

    events = []
    for it in calendar.Items:
        try:
            conversation_id = str(it.ConversationID)
            subject = str(it.Subject)
            creation_time = datetime.fromtimestamp(it.CreationTime.timestamp())
            last_modification_time = datetime.fromtimestamp(it.LastModificationTime.timestamp())
            start_timestamp = datetime.fromtimestamp(it.Start.timestamp())
            end_timestamp = datetime.fromtimestamp(it.Start.timestamp() + 60 * it.Duration)

            events.append(
                {"case:concept:name": conversation_id, "case:subject": subject, "time:timestamp": creation_time,
                 "concept:name": "Meeting Created"})

            if last_modification_time != creation_time:
                events.append({"case:concept:name": conversation_id, "case:subject": subject,
                               "time:timestamp": last_modification_time,
                               "concept:name": "Last Change of Meeting"})

            events.append(
                {"case:concept:name": conversation_id, "case:subject": subject, "time:timestamp": start_timestamp,
                 "concept:name": "Meeting Started"})
            events.append(
                {"case:concept:name": conversation_id, "case:subject": subject, "time:timestamp": end_timestamp,
                 "concept:name": "Meeting Completed"})
        except:
            pass
        if progress is not None:
            progress.update()

    if progress is not None:
        progress.close()

    dataframe = pd.DataFrame(events)
    dataframe["@@index"] = dataframe.index
    dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
    dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
    dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])

    return dataframe