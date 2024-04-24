class DiagramAgent:
    def __init__(self, key, info, actions, key_delimiter = '/'):
        self.key = key
        self.info = info
        self.key_delimiter = key_delimiter

    def get_info(self):
        return self.key + ": " + self.info

    def has_key(self, key):
        return (key in self.key) or (key in self.key.split(self.key_delimiter))


class Diagram:
    def __init__(self, name="", meta={}, agents=[]):
        self.name = name
        self.meta = meta
        self.agents = agents

    def get_agents(self):
        return self.agents

    def get_agent_keys(self):
        return [agent.key for agent in self.get_agents()]

    def get_agent_by_key(self, key):
        return [a for a in self.agents if a.has_key(key)][0]