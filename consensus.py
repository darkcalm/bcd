class TextConsensus:
    def __init__(self):
        pass


class DrawConsensus:
    def __init__(self):
        pass
        

'''

import re
from functools import reduce
from operator import iconcat

def texts_to_query(text, agent):
    tf = [q.strip(' ') for q in re.split(r"(?<!\\)"+self.delimiter, tf)]

    if len(tf) == len(diagram.get_agents()):
        return [(a.key, tf[i]) for i, a in enumerate(diagram.get_agents())]

    return [(q.split(' ', 1)[0], q.split(' ', 1)[1:]) for q in tf if (len(q.split(' ', 1)) > 1) and (q.split(' ', 1)[0] in diagram.get_agent_keys())]

def amend_querys(query):
    return {k:v for (k, v) in reduce(iconcat, query, [])}

def query_to_brackets(query):
    return self.delimiter.join([(query[k] if k in query else '')
                           for k in diagram.get_agent_keys()])

texts = [texts] if isinstance(texts, str) else texts

return query_to_brackets(
    amend_querys(
        [texts_to_query(tf) for tf in texts]
    )
)
'''

