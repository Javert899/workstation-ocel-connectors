from wocelconnectors.algo.connectors.variants import chrome_history, firefox_history, github_repo, outlook_calendar, outlook_mail_extractor, windows_events


def apply(variant, parameters0=None):
    if parameters0 is None:
        parameters0 = {}

    parameters = {}

    for param in parameters0:
        if parameters0[param] is not None and parameters0[param] != "" and parameters0[param] != " ":
            parameters[param] = parameters0[param]

    if variant == "chrome_history":
        return chrome_history.apply(parameters)
    elif variant == "firefox_history":
        return firefox_history.apply(parameters)
    elif variant == "github_repo":
        return github_repo.apply(parameters)
    elif variant == "outlook_calendar":
        return outlook_calendar.apply(parameters)
    elif variant == "outlook_mail_extractor":
        return outlook_mail_extractor.apply(parameters)
    elif variant == "windows_events":
        return windows_events.apply(parameters)
