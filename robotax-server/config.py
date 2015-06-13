from os.path import expanduser
HOME = expanduser("~")

LOCAL_PATH = "{}/TMPDOCS/".format(HOME) + "{}"

GINI_URL = "https://api.gini.net/documents"
GINI_USER, GINI_PASSWD = 'burda-hackday-01:q_NoORwCvgZAqgNQiqlAVSV7QCw'.split(':')

GINI_HEADERS = {'X-User-Identifier': 'mfcabrera', 'Accept': 'application/vnd.gini.v1+json'}
